from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
db_string = os.getenv('DATABASE_URL')

engine = create_engine(db_string)




