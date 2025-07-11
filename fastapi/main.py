from fastapi import FastAPI, HTTPException
from data_proces import enter_data
import logging
from sqlmodel import SQLModel
# from models import TestUser # You have to import the model instances before writing the create_all , since python doesn't run the code perfectly 
from db_schema import engine
import uvicorn

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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
        logger.info("Data insertion completed")
        return {"Entered": "Data inserted successfully"}
    except Exception as e:
        logger.error(f"Data insertion failed: {str(e)}")
        raise HTTPException(status_code=500,detail=f"Data insertion failed: {str(e)}")




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)