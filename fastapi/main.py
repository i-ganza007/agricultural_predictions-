from fastapi import FastAPI, HTTPException , Query
from data_proces import enter_data , Session
import logging
from sqlalchemy import text
from typing import Any, List , Dict 
from pydantic import BaseModel , Field
from sqlmodel import SQLModel
# from models import TestUser # You have to import the model instances before writing the create_all , since python doesn't run the code perfectly 
from db_schema import engine
import uvicorn
from database_procedures import create_stored_procedures_and_triggers
from models import Environment , Items ,Areas , Yield
from sqlmodel_basecrud import BaseRepository

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


with Session(engine) as session:
    environment = BaseRepository(db=session,model=Environment)
    items = BaseRepository(db=session,model=Items)
    areas = BaseRepository(db=session,model=Areas)
    yields = BaseRepository(db=session,model=Yield)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine) # Every model that inherits from SQLModel has metadata , every model that has a table = true has a metadata attribute
    create_stored_procedures_and_triggers()  # This creates our stored procedures
# This MetaData object at SQLModel.metadata has a create_all() method.
#It takes an engine and uses it to create the database and all the tables registered in this MetaData object.
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
        raise HTTPException(status_code=500,detail=f"Data insertion failed: {str(e)}")

class ItemsInput(BaseModel):
    item_name:str  

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
    temp:float
    average_rai: float = Field(alias="rai")
    pesticides_tavg: float = Field(alias="tavg")
    class Config:
        allow_population_by_field_name = True

# GET LAST ENTRIES
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
    
# GET ALL REQUESTS
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

# GET A SINGLE RECORD
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

# UPDATE A SINGLE RECORD 

@app.put('/items/update/{id}')
def update_item(req:ItemUpdate,id:int):
    try:
        item_update = items.get(item_id=id)
        item_update.item_name = req.item_name
        items.update(item_update)
        return f'Updated Item {id}'
    except Exception as e:
        return e

# @app.put('/areas/update/{id}')
# def update_areas(req,id):
#     area_update = areas.get(area_id=id)
#     area_update.area_name = req.area_name
#     areas.update(area_update)
#     return f'Updated Areas {id}'

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

# CREATE AND ADD A SINGLE RECORD

@app.post('/items/add')
def create_item(req:ItemsInput):
    try:
        items.create(Items(item_name=req.item_name))
        return f'Added successfully'
    except Exception as e:
        return e

# @app.post('/areas/add') # Double check !!!!
# def create_areas(req:Areas):
#     areas.create(Areas(area_id=req.area_id,area_name=req.area_name))
#     return f'Added successfully'

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


# DELETE RECORDS

@app.delete('/items/delete/{id}')
def delete_items(id):
    try:
        items.delete(items.get(item_id=id))
        return f'Deleted {id} in items'
    except Exception as e:
        return e
# Since maybe having some secondary keys 
# @app.delete('/areas/delete/{id}')
# def delete_areas(id):
#     try:
#         areas.delete(areas.get(id=id))
#         return f'Deleted {id} in areas'
#     except Exception as e:
#         return e

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








if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)