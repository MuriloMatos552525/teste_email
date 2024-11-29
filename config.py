# config.py
import json

with open('config.json') as config_file:
    config = json.load(config_file)

SECRET_KEY = config["SECRET_KEY"]
DB_SERVER = config["DB_SERVER"]
DB_NAME = config["DB_NAME"]
DB_USER = config["DB_USER"]
DB_PASSWORD = config["DB_PASSWORD"]
ALGORITHM = config.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
DB_DRIVER = config.get("DB_DRIVER", 'ODBC Driver 17 for SQL Server')
