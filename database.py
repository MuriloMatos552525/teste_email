# database.py
import urllib
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD, DB_DRIVER

# Monta os parâmetros da string de conexão
params = urllib.parse.quote_plus(
    f'DRIVER={{{DB_DRIVER}}};'
    f'SERVER={DB_SERVER};'
    f'DATABASE={DB_NAME};'
    f'UID={DB_USER};'
    f'PWD={DB_PASSWORD};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

DATABASE_URL = f'mssql+pyodbc:///?odbc_connect={params}'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
