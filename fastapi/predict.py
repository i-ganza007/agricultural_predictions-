import requests
import gzip
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Base URL of the FastAPI app
BASE_URL = "http://127.0.0.1:8000"

# Load the trained model
with gzip.open('best_model.pkl.gz', 'rb') as f:
    model = pickle.load(f)

def fetch_latest_environment():
    try:
        response = requests.get(f"{BASE_URL}/environment/latest")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching latest environment: {e}")
        return None

def fetch_area_name(area_id):
    try:
        response = requests.get(f"{BASE_URL}/areas/{area_id}")
        response.raise_for_status()
        return response.json().get("area_name")
    except requests.RequestException as e:
        print(f"Error fetching area {area_id}: {e}")
        return None

def fetch_all_areas():
    try:
        response = requests.get(f"{BASE_URL}/areas")
        response.raise_for_status()
        return [area["area_name"] for area in response.json()]
    except requests.RequestException as e:
        print(f"Error fetching areas: {e}")
        return []

def fetch_all_items():
    try:
        response = requests.get(f"{BASE_URL}/items")
        response.raise_for_status()
        return [item["item_name"] for item in response.json()]
    except requests.RequestException as e:
        print(f"Error fetching items: {e}")
        return []

def fetch_latest_item():
    try:
        response = requests.get(f"{BASE_URL}/items/latest")
        response.raise_for_status()
        return response.json().get("item_name")
    except requests.RequestException as e:
        print(f"Error fetching latest item: {e}")
        return None

def main():
    # Fetch the latest environment entry
    env_data = fetch_latest_environment()
    if not env_data:
        print("Failed to fetch latest environment data")
        return

    # Extract data
    area_id = env_data.get("area_id")
    year = env_data.get("year")
    average_rai = env_data.get("average_rai")
    pesticides_tavg = env_data.get("pesticides_tavg")
    temp = env_data.get("temp")

    # Fetch area_name
    area_name = fetch_area_name(area_id)
    if not area_name:
        print("Failed to fetch area_name")
        return

    # Fetch all areas and items for encoding
    all_areas = fetch_all_areas()
    all_items = fetch_all_items()
    if not all_areas or not all_items:
        print("Failed to fetch areas or items for encoding")
        return

    # Fetch the latest item
    item_name = fetch_latest_item()
    if not item_name:
        print("Failed to fetch latest item")
        return

    # Create label encoders
    area_encoder = LabelEncoder().fit(all_areas)
    item_encoder = LabelEncoder().fit(all_items)

    # Encode categorical features
    encoded_area = area_encoder.transform([area_name])[0]
    encoded_item = item_encoder.transform([item_name])[0]

    # Prepare input for model with correct feature order
    input_data = pd.DataFrame([{
        'average_rain_fall_mm_per_year': average_rai,
        'pesticides_tonnes': pesticides_tavg,
        'avg_temp': temp,
        'Item': encoded_item,
        'Area': encoded_area,
        'Year': year
    }])

    # Make prediction
    try:
        prediction = model.predict(input_data)[0]
        fetch_latest_item()
        print(f"Preparing prediction for {area_name}, {item_name}, {year}")
        print(f"Predicted hg/ha_yield: {float(prediction)}")
    except Exception as e:
        print(f"Prediction failed: {e}")

if __name__ == "__main__":
    main()
