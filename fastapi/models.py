from sqlmodel import SQLModel, Field
# from typing import Optional

class TestUser(SQLModel, table=True):
    id : int= Field(default=None, primary_key=True)
    name: str
    age: int
