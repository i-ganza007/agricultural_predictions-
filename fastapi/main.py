from re import L
from fastapi import FastAPI, HTTPException , Depends
from data_proces import enter_data , Session
import logging
from typing import Any, List , Dict 
from pydantic import BaseModel , Field
from sqlmodel import SQLModel
# from models import TestUser # You have to import the model instances before writing the create_all , since python doesn't run the code perfectly 
from db_schema import engine
import uvicorn
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
    

class EnvironmentInput(BaseModel):
    year: int
    temp: float
    rai: float = Field(alias="rai")
    tavg: float = Field(alias="tavg")
    area_id: int

class YieldIn(BaseModel):
    area_id: int
    item_id: int
    year: int
    hg: float
    
# GET ALL REQUESTS
@app.get('/items')
def get_all_items() -> List[Dict[str | int , Any]]:
    return items.get_all()

@app.get('/areas')
def get_all_areas() -> List[Dict[str | int,Any]]:
    return areas.get_all()

@app.get('/environment')
def get_all_environment() ->  List[Dict[str,Any]]:
    return environment.get_all()

@app.get('/yield')
def get_all_yields()-> List[Dict[str,Any]]:
    return yields.get_all()

# GET A SINGLE RECORD
@app.get('/items/{id}')
def get_single_items(id)-> Dict[str,Any]:
    return items.get(item_id=id)

@app.get('/areas/{id}')
def get_single_areas(id)-> Dict[str | int,Any]:
    return areas.get(area_id=id)

@app.get('/environment/{id}')
def get_single_environment(id) ->Dict[str,Any]:
    return environment.get(area_id=id)

@app.get('/yield/{id}')
def get_single_yields(id:int)-> Dict[str,Any]:
    return yields.get(area_id=id)

# UPDATE A SINGLE RECORD 

@app.patch('/items/update/{id}')
def update_item(id):
    pass

@app.patch('/areas/update/{id}')
def update_areas(id):
    pass

@app.patch('/environment/update/{id}')
def update_environment(id):
    pass

@app.patch('/yield//update/{id}')
def update_item(id):
    pass

# CREATE AND ADD A SINGLE RECORD

@app.post('/items/add')
def create_item(req:Items):
    items.create(Items(item_id=req.item_id,item_name=req.item_name))
    return f'Added successfully'

@app.post('/areas/add') # Double check !!!!
def create_areas(req:Areas):
    areas.create(Areas(area_id=req.area_id,area_name=req.area_name))
    return f'Added successfully'

@app.post('/environment/add')
def create_environment(req:EnvironmentInput):
    env = Environment(
        year=req.year,
        temp=req.temp,
        average_rai=req.rai,
        pesticides_tavg=req.tavg,
        area_id=req.area_id
    )
    environment.create(env)
    return f'Added successfully'

@app.post('/yield/add')
def create_yield(req: YieldIn):
    yiel = Yield(
        area_id=req.area_id,
        item_id=req.item_id,
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









if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)