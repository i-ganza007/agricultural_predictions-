from fastapi import FastAPI
from sqlmodel import SQLModel
from models import TestUser
from db_schema import engine
import uvicorn

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"crosix": "Connected"}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)