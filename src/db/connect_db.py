from sqlalchemy import create_engine
import urllib

def connectDB():
    ## Connecting to the SQL Server
    driver = "{ODBC Driver 17 for SQL Server}"
    server = "YH-PC"
    database = "Finance"

    connection_string = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(f'DRIVER={driver};SERVER={server};DATABASE={database};trusted_connection=yes')}"
    engine  = create_engine(connection_string)
    return engine 