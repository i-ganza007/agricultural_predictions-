from fastapi import FastAPI, HTTPException , Query
from data_proces import enter_data , Session
import logging
from sqlalchemy import text
from typing import Any, List , Dict 
from pydantic import BaseModel , Field
from sqlmodel import SQLModel
from db_schema import engine
import uvicorn
import gzip
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from database_procedures import create_stored_procedures_and_triggers
from models import Environment , Items ,Areas , Yield
from sqlmodel_basecrud import BaseRepository
from prediction_logger import prediction_logger

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model
try:
    with gzip.open('best_model.pkl.gz', 'rb') as f:
        ml_model = pickle.load(f)
    logger.info("Machine learning model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ML model: {e}")
    ml_model = None

# Dependency to get a database session
with Session(engine) as session:
    environment = BaseRepository(db=session, model=Environment)
    items = BaseRepository(db=session, model=Items)
    areas = BaseRepository(db=session, model=Areas)
    yields = BaseRepository(db=session, model=Yield)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    create_stored_procedures_and_triggers()
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

@app.get('/items/latest')
def get_latest_items() :
    try:
        length=  len(list(items.get_all()))
        return items.get_all()[length-1]
    except Exception as e:
        return e
@app.get('/environment/latest')
def get_latest_environment() :
    try:
        length=  len(list(environment.get_all()))
        return environment.get_all()[length-1]
    except Exception as e:
        return e
@app.get('/yield/latest')
def get_latest_yield() :
    try:
        length=  len(list(yields.get_all()))
        return yields.get_all()[length-1]
    except Exception as e:
        return e
@app.get('/areas/latest')
def get_latest_areas() :
    try:
        length=  len(list(areas.get_all()))
        return areas.get_all()[length-1]
    except Exception as e:
        return e
    
@app.get('/items')
def get_all_items() -> List[Dict[str | int , Any]]:
    try:    
        return items.get_all()
    except Exception as e:
        return e

@app.get('/areas')
def get_all_areas() -> List[Dict[str | int,Any]]:
    try:
        return areas.get_all()
    except Exception as e:
        return e

@app.get('/environment')
def get_all_environment() ->  List[Dict[str,Any]]:
    try:
        return environment.get_all()
    except Exception as e:
        return e

@app.get('/yield')
def get_all_yields()-> List[Dict[str,Any]]:
    try:
        return yields.get_all()
    except Exception as e:
        return e

@app.get('/items/{id}')
def get_single_items(id)-> Dict[str,Any]:
    try:
        return items.get(item_id=id)
    except Exception as e:
        return e

@app.get('/areas/{id}')
def get_single_areas(id)-> Dict[str | int,Any]:
    try:
        return areas.get(area_id=id)
    except Exception as e:
        return e

@app.get('/environment/{id}')
def get_single_environment(id) ->Dict[str,Any]:
    try:
        return environment.get(area_id=id)
    except Exception as e:
        return e

@app.get('/yield/{id}')
def get_single_yields(id:int)-> Dict[str,Any]:
    try:
        return yields.get(area_id=id)
    except Exception as e:
        return e

@app.put('/items/update/{id}')
def update_item(req:ItemUpdate,id:int):
    try:
        item_update = items.get(item_id=id)
        item_update.item_name = req.item_name
        items.update(item_update)
        return f'Updated Item {id}'
    except Exception as e:
        return e

@app.put('/environment/update/{id}/{year}')
def update_environment(req:EnvUpdate,id:int,year:int):
    try:
        env_update = environment.get(area_id=id,year=year)
        env_update.average_rai = req.average_rai
        env_update.pesticides_tavg = req.pesticides_tavg   
        env_update.temp = req.temp
        environment.update(env_update)
        return f'Updated Environment {id}'
    except Exception as e:
        return e

@app.put('/yield/update/{area_id}/{item_id}/{year}')
def update_yield(req:YieldIn,area_id,item_id,year):
    try:
        yield_update = yields.get(area_id=area_id,item_id=item_id,year=year)
        yield_update.hg_per_ha_yield = req.hg_per_ha_yield
        yields.update(yield_update)
        return f'Updated Yield {id}'
    except Exception as e:
        return e

@app.post('/items/add')
def create_item(req:ItemsInput):
    try:
        items.create(Items(item_name=req.item_name))
        return f'Added successfully'
    except Exception as e:
        return e

@app.post('/environment/add/{id}')
def create_environment(req:EnvironmentInput,id:int):
    try:
        env = Environment(year=req.year,temp=req.temp,average_rai=req.rai,pesticides_tavg=req.tavg,area_id=id)
        environment.create(env)
        return f'Added successfully'
    except Exception as e:
        return e

@app.post('/yield/add/{area_id}/{item_id}')
def create_yield(req: YieldIn,area_id,item_id):
    try:
        yiel = Yield(area_id=area_id,item_id=item_id,year=req.year,hg_per_ha_yield=req.hg)
        yields.create(yiel)  
        return f'Added successfully'
    except Exception as e:
        return e


@app.delete('/items/delete/{id}')
def delete_items(id):
    try:
        items.delete(items.get(item_id=id))
        return f'Deleted {id} in items'
    except Exception as e:
        return e

@app.delete('/environment/delete/{area_id}/{year}') 
def delete_environment(area_id,year):
    try:
        environment.delete(environment.get(area_id=area_id,year=year))
        return f'Deleted {area_id} in {year} in environment'
    except Exception as e:
        return e

@app.delete('/yields/delete/{area_id}/{item_id}/{year}')
def delete_yields(area_id,item_id,year):
    try:
        yields.delete(yields.get(item_id=item_id,area_id=area_id,year=year))
        return f'Deleted {area_id} in {areas.get(area_id=area_id)} from {year} in yields'
    except Exception as e:
        return e

@app.get("/procedures/item_yield_average/{item_id}")
def get_item_yield_average(item_id: int):
    """Endpoint that uses the CalculateItemYieldAverage stored procedure"""
    try:
        with Session(engine) as session:
            result = session.execute(
                text("CALL CalculateItemYieldAverage(:item_id)"),
                {"item_id": item_id}
            ).fetchall()
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/procedures/area_environment_stats/{area_id}")
def get_area_environment_stats(area_id: int):
    """Endpoint that uses the GetAreaEnvironmentStats stored procedure"""
    try:
        with Session(engine) as session:
            result = session.execute(
                text("CALL GetAreaEnvironmentStats(:area_id)"),
                {"area_id": area_id}
            ).fetchall()
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/procedures/predict_yield/{area_id}/{item_id}")
def predict_yield(
    area_id: int,
    item_id: int,
    temp: float = Query(...),
    rain: float = Query(...),
    pesticides: float = Query(...)
):
    """Endpoint that uses the PredictYield stored procedure"""
    try:
        with Session(engine) as session:
            result = session.execute(
                text("CALL PredictYield(:area_id, :item_id, :temp, :rain, :pesticides)"),
                {
                    "area_id": area_id,
                    "item_id": item_id,
                    "temp": temp,
                    "rain": rain,
                    "pesticides": pesticides
                }
            ).scalar()
            return {"predicted_yield": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/procedures/top_producing_areas/{item_id}/{year}")
def get_top_producing_areas(
    item_id: int,
    year: int,
    limit: int = Query(10, gt=0, le=100)
):
    """Endpoint that uses the FindTopProducingAreas stored procedure"""
    try:
        with Session(engine) as session:
            result = session.execute(
                text("CALL FindTopProducingAreas(:item_id, :year, :limit)"),
                {"item_id": item_id, "year": year, "limit": limit}
            ).fetchall()
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/ml")
def predict_with_ml_model(
    area_id: int,
    item_id: int,
    year: int,
    temp: float = Query(..., description="Temperature"),
    rain: float = Query(..., description="Average rainfall"),
    pesticides: float = Query(..., description="Pesticides usage")
):
    """Make prediction using the trained ML model with database data for encoding"""
    if ml_model is None:
        raise HTTPException(status_code=500, detail="ML model not loaded")
    
    try:
        # Create a fresh session for this request
        with Session(engine) as fresh_session:
            # Create fresh repository instances
            fresh_areas = BaseRepository(db=fresh_session, model=Areas)
            fresh_items = BaseRepository(db=fresh_session, model=Items)
            
            # Fetch area and item
            area = fresh_areas.get(area_id=area_id)
            if not area:
                raise HTTPException(status_code=404, detail="Area not found")
            
            item = fresh_items.get(item_id=item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # Get all areas and items for encoding
            all_areas_objects = fresh_areas.get_all()
            all_items_objects = fresh_items.get_all()
            
            # Extract names from objects - handle both dict and object formats
            all_areas = []
            for a in all_areas_objects:
                if isinstance(a, dict):
                    all_areas.append(a["area_name"])
                else:
                    all_areas.append(a.area_name)
                    
            all_items = []
            for i in all_items_objects:
                if isinstance(i, dict):
                    all_items.append(i["item_name"])
                else:
                    all_items.append(i.item_name)
            
            # Create label encoders
            area_encoder = LabelEncoder().fit(all_areas)
            item_encoder = LabelEncoder().fit(all_items)
            
            # Get area and item names - handle both dict and object formats
            area_name = area.area_name if hasattr(area, 'area_name') else area["area_name"]
            item_name = item.item_name if hasattr(item, 'item_name') else item["item_name"]
            
            # Encode categorical features
            encoded_area = area_encoder.transform([area_name])[0]
            encoded_item = item_encoder.transform([item_name])[0]
            
            # Prepare input for model
            input_data = pd.DataFrame([{
                'average_rain_fall_mm_per_year': rain,
                'pesticides_tonnes': pesticides,
                'avg_temp': temp,
                'Item': encoded_item,
                'Area': encoded_area,
                'Year': year
            }])
            
            # Make prediction
            prediction = ml_model.predict(input_data)[0]
            
            # Prepare response
            response_data = {
                "area_id": area_id,
                "item_id": item_id,
                "area_name": area_name,
                "item_name": item_name,
                "year": year,
                "input_data": {
                    "temperature": temp,
                    "rainfall": rain,
                    "pesticides": pesticides
                },
                "predicted_yield_hg_per_ha": float(prediction),
                "model_used": "trained_ml_model"
            }
            
            # Save prediction to MongoDB
            try:
                prediction_saved = prediction_logger.log_prediction(response_data)
                if prediction_saved:
                    logger.info(f"Prediction saved to MongoDB for area_id={area_id}, item_id={item_id}")
                    response_data["mongodb_logged"] = True
                else:
                    logger.warning("Failed to save prediction to MongoDB")
                    response_data["mongodb_logged"] = False
            except Exception as log_error:
                logger.warning(f"Error saving prediction to MongoDB: {log_error}")
                response_data["mongodb_logged"] = False
            
            return response_data
            
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/predictions/history")
def get_prediction_history(
    area_id: int = Query(None, description="Filter by area ID"),
    item_id: int = Query(None, description="Filter by item ID"), 
    limit: int = Query(100, ge=1, le=1000, description="Number of predictions to retrieve")
):
    """Retrieve prediction history from MongoDB"""
    try:
        history = prediction_logger.get_prediction_history(
            area_id=area_id,
            item_id=item_id, 
            limit=limit
        )
        return {
            "total_predictions": len(history),
            "predictions": history,
            "mongodb_available": prediction_logger.predictions_collection is not None
        }
    except Exception as e:
        logger.error(f"Failed to retrieve prediction history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prediction history: {str(e)}")

@app.on_event("shutdown")
def on_shutdown():
    """Cleanup on application shutdown"""
    try:
        prediction_logger.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.warning(f"Error closing MongoDB connection: {e}")
    logger.info("Application shutdown completed")

@app.get("/debug/data_structure")
def debug_data_structure():
    """Debug endpoint to check data structure"""
    try:
        # Get sample data
        sample_areas = areas.get_all()[:2] if areas.get_all() else []
        sample_items = items.get_all()[:2] if items.get_all() else []
        
        return {
            "areas_count": len(areas.get_all()) if areas.get_all() else 0,
            "items_count": len(items.get_all()) if items.get_all() else 0,
            "sample_area_type": type(sample_areas[0]).__name__ if sample_areas else "None",
            "sample_item_type": type(sample_items[0]).__name__ if sample_items else "None",
            "sample_area_data": str(sample_areas[0]) if sample_areas else "None",
            "sample_item_data": str(sample_items[0]) if sample_items else "None",
            "ml_model_loaded": ml_model is not None
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/mongodb_status")
def check_mongodb_status():
    """Check MongoDB connection status"""
    try:
        if prediction_logger.predictions_collection is not None:
            # Try to count documents to test connection
            count = prediction_logger.predictions_collection.count_documents({})
            return {
                "mongodb_connected": True,
                "predictions_count": count,
                "database": "agri-yield",
                "collection": "predictions"
            }
        else:
            return {
                "mongodb_connected": False,
                "error": "MongoDB connection not established",
                "predictions_count": 0
            }
    except Exception as e:
        return {
            "mongodb_connected": False,
            "error": str(e),
            "predictions_count": 0
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
