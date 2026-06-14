from sqlalchemy import create_engine
import urllib
from config.settings import DB_DRIVER, DB_SERVER, DB_NAME

def connectDB():
    ## Connecting to the SQL Server
    driver = f"{{DB_DRIVER}}"
    server =  DB_SERVER
    database = DB_NAME

    connection_string = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(f'DRIVER={driver};SERVER={server};DATABASE={database};trusted_connection=yes')}"
    engine  = create_engine(connection_string)
    return engine 