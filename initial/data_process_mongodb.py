from dotenv import load_dotenv
import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Load environment variables from .env file
load_dotenv()

try:
    # Connect to MongoDB Atlas using environment variable
    client = MongoClient(os.getenv('MONGO_URL'))
    db = client['agri-yield']  # Use the 'agri-yield' database

    # Create unique indexes to prevent duplicates
    db.environment.create_index([("area_id", 1), ("year", 1)], unique=True)
    db.yields.create_index([("area_id", 1), ("item_id", 1), ("year", 1)], unique=True)

    # Read CSV
    df = pd.read_csv('yield_df.csv')

    # Insert unique areas
    areas_collection = db.areas
    unique_areas = df['Area'].unique()
    areas = [{"area_name": area.strip()} for area in unique_areas if isinstance(area, str)]
    area_results = areas_collection.insert_many(areas)
    area_id_map = {area["area_name"]: area_id for area, area_id in zip(areas, area_results.inserted_ids)}

    # Insert unique items
    items_collection = db.items
    unique_items = df['Item'].unique()
    items = [{"item_name": item.strip()} for item in unique_items if isinstance(item, str)]
    item_results = items_collection.insert_many(items)
    item_id_map = {item["item_name"]: item_id for item, item_id in zip(items, item_results.inserted_ids)}

    # Insert environment data (unique by area_id, year)
    environment_collection = db.environment
    environment_docs = []
    environment_set = set()  # Track unique (area_id, year) combinations
    for _, row in df.iterrows():
        area_name = row['Area']
        year = int(row['Year']) if pd.notnull(row['Year']) else None
        if pd.notnull(area_name) and year is not None:
            area_id = area_id_map.get(area_name)
            if area_id and (area_id, year) not in environment_set:
                environment_docs.append({
                    "area_id": area_id,
                    "year": year,
                    "average_rain": float(row['average_rain_fall_mm_per_year']) if pd.notnull(row['average_rain_fall_mm_per_year']) else None,
                    "pesticides_tavg": float(row['pesticides_tonnes']) if pd.notnull(row['pesticides_tonnes']) else None,
                    "temp": float(row['avg_temp']) if pd.notnull(row['avg_temp']) else None
                })
                environment_set.add((area_id, year))
    if environment_docs:
        try:
            environment_collection.insert_many(environment_docs, ordered=False)
        except DuplicateKeyError as e:
            print(f"Duplicate environment entries skipped: {e}")

    # Insert yield data
    yield_collection = db.yields
    yield_docs = []
    for _, row in df.iterrows():
        area_name = row['Area']
        item_name = row['Item']
        year = int(row['Year']) if pd.notnull(row['Year']) else None
        if pd.notnull(area_name) and pd.notnull(item_name) and year is not None:
            area_id = area_id_map.get(area_name)
            item_id = item_id_map.get(item_name)
            if area_id and item_id:
                yield_docs.append({
                    "area_id": area_id,
                    "item_id": item_id,
                    "year": year,
                    "hg_per_ha_yield": float(row['hg/ha_yield']) if pd.notnull(row['hg/ha_yield']) else None
                })
    if yield_docs:
        try:
            yield_collection.insert_many(yield_docs, ordered=False)
        except DuplicateKeyError as e:
            print(f"Duplicate yield entries skipped: {e}")

    # Verify the counts
    print(f"Inserted {areas_collection.count_documents({})} areas")
    print(f"Inserted {items_collection.count_documents({})} items")
    print(f"Inserted {environment_collection.count_documents({})} environment records")
    print(f"Inserted {yield_collection.count_documents({})} yield records")
    print("MongoDB data inserted successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    client.close()
    print("MongoDB connection closed.")
