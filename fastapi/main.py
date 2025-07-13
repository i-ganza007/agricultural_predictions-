from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, SQLModel
from typing import Any, List, Dict
from pydantic import BaseModel, Field
import logging
from models import Environment, Items, Areas, Yield
from sqlmodel_basecrud import BaseRepository
from db_schema import engine
import uvicorn
from data_proces import enter_data
import pickle
import gzip
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model
with gzip.open('best_model.pkl.gz', 'rb') as f:
    model = pickle.load(f)

# Dependency to get a database session
with Session(engine) as session:
    environment = BaseRepository(db=session, model=Environment)
    items = BaseRepository(db=session, model=Items)
    areas = BaseRepository(db=session, model=Areas)
    yields = BaseRepository(db=session, model=Yield)

# Define get_session for prediction endpoint
def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"crosix": "Connected"}

@app.post('/enter_recs')
def insert_recs():
    logger.info("Received POST request to /enter_recs")
    try:
        enter_data()
        return {"Entered": "Data inserted successfully"}
    except Exception as e:
        logger.error(f"Data insertion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data insertion failed: {str(e)}")

# Pydantic models
class ItemsInput(BaseModel):
    item_name: str

class EnvironmentInput(BaseModel):
    year: int
    temp: float
    rai: float = Field(alias="rai")
    tavg: float = Field(alias="tavg")

class YieldIn(BaseModel):
    hg_per_ha_yield: float = Field(alias='hg')

class ItemUpdate(BaseModel):
    item_name: str

class EnvUpdate(BaseModel):
    temp: float
    average_rai: float = Field(alias="rai")
    pesticides_tavg: float = Field(alias="tavg")
    class Config:
        allow_population_by_field_name = True

# GET LAST ENTRIES
@app.get('/items/latest')
def get_latest_items():
    length = len(list(items.get_all()))
    return items.get_all()[length-1]

@app.get('/environment/latest')
def get_latest_environment():
    length = len(list(environment.get_all()))
    return environment.get_all()[length-1]

@app.get('/yield/latest')
def get_latest_yield():
    length = len(list(yields.get_all()))
    return yields.get_all()[length-1]

@app.get('/areas/latest')
def get_latest_areas():
    length = len(list(areas.get_all()))
    return areas.get_all()[length-1]

# GET ALL REQUESTS
@app.get('/items')
def get_all_items() -> List[Dict[str | int, Any]]:
    return items.get_all()

@app.get('/areas')
def get_all_areas() -> List[Dict[str | int, Any]]:
    return areas.get_all()

@app.get('/environment')
def get_all_environment() -> List[Dict[str, Any]]:
    return environment.get_all()

@app.get('/yield')
def get_all_yields() -> List[Dict[str, Any]]:
    return yields.get_all()

# GET A SINGLE RECORD
@app.get('/items/{id}')
def get_single_items(id) -> Dict[str, Any]:
    return items.get(item_id=id)

@app.get('/areas/{id}')
def get_single_areas(id) -> Dict[str | int, Any]:
    return areas.get(area_id=id)

@app.get('/environment/{id}')
def get_single_environment(id) -> Dict[str, Any]:
    return environment.get(area_id=id)

@app.get('/yield/{id}')
def get_single_yields(id: int) -> Dict[str, Any]:
    return yields.get(area_id=id)

# UPDATE A SINGLE RECORD
@app.put('/items/update/{id}')
def update_item(req: ItemUpdate, id: int):
    item_update = items.get(item_id=id)
    item_update.item_name = req.item_name
    items.update(item_update)
    return f'Updated Item {id}'

@app.put('/environment/update/{id}/{year}')
def update_environment(req: EnvUpdate, id: int, year: int):
    env_update = environment.get(area_id=id, year=year)
    env_update.average_rai = req.average_rai
    env_update.pesticides_tavg = req.pesticides_tavg
    env_update.temp = req.temp
    environment.update(env_update)
    return f'Updated Environment {id}'

@app.put('/yield/update/{area_id}/{item_id}/{year}')
def update_yield(req: YieldIn, area_id, item_id, year):
    yield_update = yields.get(area_id=area_id, item_id=item_id, year=year)
    yield_update.hg_per_ha_yield = req.hg_per_ha_yield
    yields.update(yield_update)
    return f'Updated Yield {id}'

# CREATE AND ADD A SINGLE RECORD
@app.post('/items/add')
def create_item(req: ItemsInput):
    items.create(Items(item_name=req.item_name))
    return f'Added successfully'

@app.post('/areas/add')
def create_areas(req: Areas):
    areas.create(Areas(area_id=req.area_id, area_name=req.area_name))
    return f'Added successfully'

@app.post('/environment/add/{id}')
def create_environment(req: EnvironmentInput, id: int):
    env = Environment(
        year=req.year,
        temp=req.temp,
        average_rai=req.rai,
        pesticides_tavg=req.tavg,
        area_id=id
    )
    environment.create(env)
    return f'Added successfully'

@app.post('/yield/add/{area_id}/{item_id}')
def create_yield(req: YieldIn, area_id, item_id):
    yiel = Yield(
        area_id=area_id,
        item_id=item_id,
        year=req.year,
        hg_per_ha_yield=req.hg
    )
    yields.create(yiel)
    return f'Added successfully'

# DELETE RECORDS
@app.delete('/items/delete/{id}')
def delete_items(id):
    items.delete(items.get(id=id))
    return f'Deleted {id} in items'

@app.delete('/areas/delete/{id}')
def delete_areas(id):
    areas.delete(areas.get(id=id))
    return f'Deleted {id} in areas'

@app.delete('/environment/delete/{id}')
def delete_environment(id):
    environment.delete(environment.get(id=id))
    return f'Deleted {id} in environment'

@app.delete('/yields/delete/{id}')
def delete_yields(id):
    yields.delete(yields.get(id=id))
    return f'Deleted {id} in yields'

# Prediction endpoint
class PredictionInput(BaseModel):
    area_name: str
    item_name: str
    year: int
    average_rainfall_mm_per_year: float = Field(alias="rai")
    pesticides_tonnes: float = Field(alias="tavg")
    avg_temp: float = Field(alias="temp")

@app.post('/predict')
def predict_yield(req: PredictionInput, session: Session = Depends(get_session)):
    try:
        # Initialize BaseRepository for Areas and Items
        area_repo = BaseRepository(db=session, model=Areas)
        item_repo = BaseRepository(db=session, model=Items)

        # Validate area_name and item_name
        area = area_repo.get_by_field(area_name=req.area_name)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {req.area_name} not found")
        item = item_repo.get_by_field(item_name=req.item_name)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {req.item_name} not found")

        # Fetch all areas and items for encoding
        all_areas = [a.area_name for a in area_repo.get_all()]
        all_items = [i.item_name for i in item_repo.get_all()]

        # Create label encoders
        area_encoder = LabelEncoder().fit(all_areas)
        item_encoder = LabelEncoder().fit(all_items)

        # Encode categorical features
        encoded_area = area_encoder.transform([req.area_name])[0]
        encoded_item = item_encoder.transform([req.item_name])[0]

        # Prepare input for model
        input_data = pd.DataFrame([{
            'Area': encoded_area,
            'Item': encoded_item,
            'Year': req.year,
            'average_rain_fall_mm_per_year': req.average_rainfall_mm_per_year,
            'pesticides_tonnes': req.pesticides_tonnes,
            'avg_temp': req.avg_temp
        }])

        # Make prediction
        prediction = model.predict(input_data)[0]

        return {"predicted_hg_per_ha_yield": float(prediction)}
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
