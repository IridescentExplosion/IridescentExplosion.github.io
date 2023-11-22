import requests
import os
import json

# List of area IDs for Indianapolis
area_ids = [
    1359173, 1359118, 56944, 1359187, 1359119, 1359180, 1359169, 713147, 1359120, 56662,
    1359186, 1359133, 1359131, 1359116, 1359123, 1359125, 1359140, 1359127, 1359185, 1359128,
    1359172, 1359184, 1359129, 56666, 1359134, 1359138, 1001390, 1359162, 1359139, 1359130,
    828783, 1359143, 1359146, 1306360, 1359170, 1359179, 56663, 1359153, 1359160, 1359161,
    1359163, 1359165, 1359181, 1359171, 1359182, 1359183, 713148, 262829, 1359178, 1001475,
    1359166, 828782, 1359176, 1359167, 1001476, 1359168, 1359175, 1359174, 262832, 1359177, 56668
]

# Function to fetch area details
def fetch_area_details(area_id):
    url = f"http://global.mapit.mysociety.org/area/{area_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to fetch, update, and save GeoJSON data
def fetch_and_save_geojson(area_id):
    # Fetch GeoJSON data
    geojson_url = f"http://global.mapit.mysociety.org/area/{area_id}.geojson"
    geojson_response = requests.get(geojson_url)

    if geojson_response.status_code == 200:
        geojson_data = geojson_response.json()

        # Fetch area details for the name
        area_details = fetch_area_details(area_id)
        if area_details and 'name' in area_details:
            # Construct a Feature with the Polygon and the name
            feature = {
                "type": "Feature",
                "properties": {
                    "name": area_details['name']
                },
                "geometry": geojson_data
            }

            # Construct a FeatureCollection
            feature_collection = {
                "type": "FeatureCollection",
                "features": [feature]
            }

            # Save the updated GeoJSON data
            file_path = f"area_{area_id}.geojson"
            with open(file_path, 'w') as file:
                json.dump(feature_collection, file)

            print(f"Updated and saved GeoJSON for area ID {area_id}")
        else:
            print(f"Name not found for area ID {area_id}")
    else:
        print(f"Failed to fetch GeoJSON data for area ID {area_id}")

# Directory for the GeoJSON files
file_dir = "geojson_files"
os.makedirs(file_dir, exist_ok=True)
os.chdir(file_dir)

# Fetching, updating, and saving GeoJSON data for each area
for area_id in area_ids:
    fetch_and_save_geojson(area_id)

print("All GeoJSON files have been updated and saved in the 'geojson_files' directory.")
