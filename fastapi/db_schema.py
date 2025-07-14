from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_string = os.getenv('DATABASE_URL')

engine = create_engine(db_string) # This helps us to manage the database connections to the strings and the remote database
# echo helps us to print the SQL statements executed and see what's happening




