import pandas as pd
from sqlmodel import Session, select
from db_schema import engine 
from models import Items, Areas, Environment, Yield , Crops , countries

data = pd.read_csv('yield_df.csv')

data['Item'] = data['Item'].str.strip().str.title()
data['Area'] = data['Area'].str.strip()

data = data.astype({
    'Year': 'int',
    'average_rain_fall_mm_per_year': 'float',
    'pesticides_tonnes': 'float',
    'avg_temp': 'float',
    'hg/ha_yield': 'float'
})

Items_dataset = data['Item']
Areas_dataset = data['Area']
Environ_dataset = data[['average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']]
Yield_dataset = data['hg/ha_yield']

def validate_item():
    crops = [i.value.lower() for i in Crops] 
    if not Items_dataset.str.lower().isin(crops).all():
        invalid_items = Items_dataset[~Items_dataset.str.lower().isin(crops)].unique()
        raise ValueError(f"items invalid: {invalid_items}")

def validate_area():
    if not Areas_dataset.isin(countries).all():
        raise ValueError(f"areas invalid: {Areas_dataset[~Areas_dataset.isin(countries)].unique()}")

def validate_years():
    if not data['Year'].between(1980, 2025).all():
        raise ValueError(f"years invalid: {data['Year'][~data['Year'].between(1980, 2025)].unique()}")

def validate_environ():
    if Environ_dataset.isna().any().any():
        raise ValueError("missing: Environ_dataset")
    if not (Environ_dataset >= 0).all().all():
        raise ValueError("Negative: Environ_dataset")

def validate_yield():
    if Yield_dataset.isna().any():
        raise ValueError("Missing : Yield_dataset")
    if not (Yield_dataset >= 0).all():
        raise ValueError("Negative : Yield_dataset")

def environ_dup():
    area_year = Environ_dataset[['Area', 'Year']].drop_duplicates()
    if len(area_year) != len(Environ_dataset):
        raise ValueError("Duplicate (Area, Year) in aggregated ")

def yield_dup():
    dup_mask = data.duplicated(subset=['Area', 'Item', 'Year'], keep=False)
    if dup_mask.any():
        duplicates = data[dup_mask].sort_values(['Area', 'Item', 'Year'])
        print("Duplicate (Area, Item, Year) combinations found:")
        print(duplicates[['Area', 'Item', 'Year']].drop_duplicates())
        raise ValueError("Duplicate (Area, Item, Year) in yield data")
    
def is_data_inserted(session: Session) -> bool:

    items_count = session.exec(select(Items)).first() is not None
    areas_count = session.exec(select(Areas)).first() is not None
    return items_count or areas_count

# def enter_data():
#     with Session(engine) as session:
#         try:

#             if is_data_inserted(session):
#                 print("Data already inserted")
#                 return
            
#             step = "validation"
#             validate_item()
#             validate_area()
#             validate_years()
#             validate_environ()
#             environ_dup()
#             yield_dup()
#             print("Data validation passed")

#             step = "Items insertion"
#             item_id_map = {}
#             for item in Items_dataset.unique():
#                 # if item in [crop.value for crop in Crops]:
#                     item_obj = Items(item_name=item)
#                     session.add(item_obj)
#                     session.flush()
#                     item_id_map[item] = item_obj.item_id
#             print(f'Done for Items: {len(item_id_map)}')

#             step = "Areas insertion"
#             area_id_map = {}
#             for area in Areas_dataset.unique():
#                 # if area in countries:
#                     area_obj = Areas(area_name=area)
#                     session.add(area_obj)
#                     session.flush()
#                     area_id_map[area] = area_obj.area_id
#             print(f'Done with Areas: {len(area_id_map)}')

#             step = "Environment insertion"
#             env_count = 0
#             for idx, row in data.iterrows():
#                 area_id = area_id_map.get(row['Area'])
#                 if (area_id and 1980 <= row['Year'] <= 2025 and
#                     all(Environ_dataset.loc[idx, col] >= 0 for col in Environ_dataset.columns)):
#                     env = Environment(
#                         year=row['Year'],
#                         average_rai=Environ_dataset.loc[idx, 'average_rain_fall_mm_per_year'],
#                         pesticides_tavg=Environ_dataset.loc[idx, 'pesticides_tonnes'],
#                         temp=Environ_dataset.loc[idx, 'avg_temp'],
#                         area_id=area_id
#                     )
#                     session.add(env)
#                     env_count += 1
#             print(f"Done with Environment: {env_count}")

#             step = "Yield insertion"
#             yield_count = 0
#             for idx, row in data.iterrows():
#                 area_id = area_id_map.get(row['Area'])
#                 item_id = item_id_map.get(row['Item'])
#                 if (area_id and item_id and 1980 <= row['Year'] <= 2025 and
#                     Yield_dataset.loc[idx] >= 0):
#                     yield_ = Yield(
#                         area_id=area_id,
#                         item_id=item_id,
#                         year=row['Year'],
#                         hg_per_ha_yield=Yield_dataset.loc[idx]
#                     )
#                     session.add(yield_)
#                     yield_count += 1
#             print(f"Done with Yield: {yield_count}")

#             session.commit()
#             print(" insertion completed successfully")

#         except Exception as e:
#             session.rollback()
#             print(f"Insertion failed {step}: {e}")
#             raise

def enter_data():
    with Session(engine) as session:
        try:

            global data  
            data = data.drop_duplicates(subset=['Area', 'Item', 'Year'], keep='first')
            if is_data_inserted(session):
                print("Data already inserted")
                return

            env_data = data.groupby(['Area', 'Year']).agg({
                'average_rain_fall_mm_per_year': 'mean',
                'pesticides_tonnes': 'mean',
                'avg_temp': 'mean'
            }).reset_index()

            print("Validating data...")
            validate_item() 
            validate_area()  
            validate_years()  
            validate_environ()  
            validate_yield() 
            
            # Check for duplicates 
            if env_data[['Area', 'Year']].duplicated().any():
                raise ValueError("Duplicate (Area, Year) in aggregated env_data")
            
            # Check yield duplicates Area  Item  Year
            yield_dup()  

            item_id_map = {}
            for item in data['Item'].unique():
                item_obj = Items(item_name=item)
                session.add(item_obj)
                session.flush()  
                item_id_map[item] = item_obj.item_id

            area_id_map = {}
            for area in data['Area'].unique():
                area_obj = Areas(area_name=area)
                session.add(area_obj)
                session.flush()
                area_id_map[area] = area_obj.area_id

            env_count = 0
            for _, row in env_data.iterrows():
                env = Environment(
                    year=row['Year'],
                    average_rai=row['average_rain_fall_mm_per_year'],
                    pesticides_tavg=row['pesticides_tonnes'],
                    temp=row['avg_temp'],
                    area_id=area_id_map[row['Area']]
                )
                session.add(env)
                env_count += 1

            yield_count = 0
            for _, row in data.iterrows():
                yield_ = Yield(
                    area_id=area_id_map[row['Area']],
                    item_id=item_id_map[row['Item']],
                    year=row['Year'],
                    hg_per_ha_yield=row['hg/ha_yield']
                )
                session.add(yield_)
                yield_count += 1

            session.commit()

        except Exception as e:
            session.rollback()

if __name__ == "__main__":
    try:
        enter_data()
    except Exception as e:
        print(f"Error: {e}")