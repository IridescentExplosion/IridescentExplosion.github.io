import requests
import os

# List of area IDs for Indianapolis / Marion County
indianapolis_area_id = 967667

# Areas covered (within) Indianapolis / Marion County
area_ids = [
    1359173, 1359118, 56944, 1359187, 1359119, 1359180, 1359169, 713147, 1359120, 56662,
    1359186, 1359133, 1359131, 1359116, 1359123, 1359125, 1359140, 1359127, 1359185, 1359128,
    1359172, 1359184, 1359129, 56666, 1359134, 1359138, 1001390, 1359162, 1359139, 1359130,
    828783, 1359143, 1359146, 1306360, 1359170, 1359179, 56663, 1359153, 1359160, 1359161,
    1359163, 1359165, 1359181, 1359171, 1359182, 1359183, 713148, 262829, 1359178, 1001475,
    1359166, 828782, 1359176, 1359167, 1001476, 1359168, 1359175, 1359174, 262832, 1359177, 56668
]

####################################################################################################
# Setup stuff
####################################################################################################
# File directory where the GeoJSON files are saved ex: area_967667.geojson
geo_data_dir = "geojson_files"
map_data_dir = "maps"
indygov_data_dir = "indygov_data"

import folium
import geopandas as gpd
import json
from folium.plugins import FeatureGroupSubGroup
from shapely.geometry import shape

# Function to calculate the centroid of a feature for placing the label
def get_centroid(geometry):
    # Ensure that the centroid coordinates are in (latitude, longitude) order
    centroid = geometry.centroid
    return (centroid.y, centroid.x)

def add_labels_geojson(feature_group, geojson_data, label_field):
    for feature in geojson_data['features']:
        geometry = shape(feature['geometry'])
        label_text = feature['properties'][label_field]
        label_location = list(geometry.centroid.coords)[0]
        folium.map.Marker(
            label_location,
            icon=folium.DivIcon(html=f'<div style="font-size: 12pt">{label_text}</div>')
        ).add_to(feature_group)

# Function to add labels from a GeoDataFrame
def add_labels_gdf(feature_group, gdf, label_field):
    for _, row in gdf.iterrows():
        label_text = row[label_field]
        label_location = list(row['geometry'].centroid.coords)[0]
        folium.Marker(
            location=label_location,
            icon=folium.DivIcon(html=f'<div style="font-size: 12pt">{label_text}</div>')
        ).add_to(feature_group)

####################################################################################################
# .geojson files from mapit.mysociety.org
####################################################################################################
# Load the GeoJSON for the main Indianapolis area
with open(os.path.join(geo_data_dir, f'area_{indianapolis_area_id}.geojson'), 'r') as file:
    indianapolis_geojson = json.load(file)

# Create a map centered at the centroid of Indianapolis
indianapolis_map = folium.Map(location=[39.7684, -86.1581], zoom_start=11)

####################################################################################################
# KML shapefile data from Indy.gov. You can download the GIS data yourself: https://data.indy.gov/datasets/IndyGIS::indy-neighborhoods/about
####################################################################################################

# Path to the Shapefile
shapefile_path = os.path.join(indygov_data_dir, 'Indy_Neighborhoods.shp')

# Read the Shapefile
gdf = gpd.read_file(shapefile_path)

# Display the first few rows of the GeoDataFrame to understand its structure
gdf.head()

# Create main feature groups for MapIt and IndyGov data, including labels
mapit_data_group = folium.FeatureGroup(name='MapIt Data', show=True).add_to(indianapolis_map)
mapit_labels_group = folium.FeatureGroup(name='MapIt - Labels', show=False).add_to(indianapolis_map)
indygov_data_group = folium.FeatureGroup(name='IndyGov Data', show=True).add_to(indianapolis_map)
indygov_labels_group = folium.FeatureGroup(name='IndyGov - Labels', show=False).add_to(indianapolis_map)

# Add GeoJSON data to sub-groups of the MapIt Data group
for area_id in area_ids:
    file_path = os.path.join(geo_data_dir, f'area_{area_id}.geojson')
    with open(file_path, 'r') as file:
        area_geojson = json.load(file)
    area_name = area_geojson['features'][0]['properties']['name']
    sub_group = FeatureGroupSubGroup(mapit_data_group, name="MapIt - " + area_name)
    folium.GeoJson(area_geojson, tooltip=area_name).add_to(sub_group)
    sub_group.add_to(indianapolis_map)  # Add the subgroup to the map

    # Assuming 'area_geojson' is a GeoJSON FeatureCollection
    for feature in area_geojson['features']:
        centroid = get_centroid(shape(feature['geometry']))
        label_text = feature['properties']['name']
        folium.Marker(
            location=centroid,
            icon=folium.DivIcon(html=f'<div style="font-size: 12pt">{label_text}</div>')
        ).add_to(mapit_labels_group)

# Add Shapefile data to sub-groups of the IndyGov Data group
for _, row in gdf.iterrows():
    area_name = row['NAME']
    sub_group = FeatureGroupSubGroup(indygov_data_group, name="IndyGov - " + area_name)
    folium.GeoJson(row['geometry'], tooltip=area_name).add_to(sub_group)
    sub_group.add_to(indianapolis_map)  # Add the subgroup to the map

# Add labels for IndyGov Data
for _, row in gdf.iterrows():
    centroid = get_centroid(row['geometry'])
    label_text = row['NAME']
    folium.Marker(
        location=centroid,
        icon=folium.DivIcon(html=f'<div style="font-size: 12pt">{label_text}</div>')
    ).add_to(indygov_labels_group)

# Add a LayerControl to toggle the groups
folium.LayerControl(collapsed=False).add_to(indianapolis_map)

# Save the map to an HTML file
html_file_path = os.path.join('index.html')
indianapolis_map.save(html_file_path)

print(f"Map with toggleable labels has been saved to {html_file_path}")