# import libraries
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

try:
    # Connect to MongoDB Atlas
    client = MongoClient('mongodb+srv://gowen:T0ujgWXW8mcxTxQi@agri.l590kwt.mongodb.net/?retryWrites=true&w=majority&appName=agri')
    db = client['agri-yield']  # Use the 'agri-yield' database

    # Create unique index on yieldData to prevent duplicates
    db.yieldData.create_index([("area_id", 1), ("crop_id", 1), ("year", 1)], unique=True)

    # Read CSV
    df = pd.read_csv('yield_df.csv')

    # Insert unique areas
    unique_areas = df['Area'].unique()
    areas = [{"area_name": area} for area in unique_areas]
    area_results = db.areas.insert_many(areas)
    area_id_map = {area["area_name"]: area_id for area, area_id in zip(areas, area_results.inserted_ids)}

    # Insert unique crops
    unique_crops = df['Item'].unique()
    crops = [{"crop_name": crop} for crop in unique_crops]
    crop_results = db.crops.insert_many(crops)
    crop_id_map = {crop["crop_name"]: crop_id for crop, crop_id in zip(crops, crop_results.inserted_ids)}

    # Insert yield data
    for _, row in df.iterrows():
        try:
            db.yieldData.insert_one({
                "area_id": area_id_map[row['Area']],
                "crop_id": crop_id_map[row['Item']],
                "year": int(row['Year']),
                "hg_ha_yield": int(row['hg/ha_yield']),
                "avg_rainfall_mm_per_year": float(row['average_rain_fall_mm_per_year']),
                "pesticides_tonnes": float(row['pesticides_tonnes']),
                "avg_temp": float(row['avg_temp'])
            })
        except DuplicateKeyError:
            print(f"Duplicate entry skipped for {row['Area']}, {row['Item']}, {row['Year']}")

    print("MongoDB data inserted successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
    print("MongoDB connection closed.")
