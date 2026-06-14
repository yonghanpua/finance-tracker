import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, inspect
from src.db.connect_db import connectDB

## Create a function to Update the SQL Table
def FuncUpdateSQLTable(df, SQLtable, engine):
    """
    Update the SQL table with a given DataFrame
    If the table exists, it will be dropped and recreated with the new data
    
    Args:
        df (pd.DataFrame): The DataFrame to upload
        SQLtable (str): The name of the SQL table
        engine: The SQLAlchemy engine object
    """
    inspector = inspect(engine)
    
    if SQLtable in inspector.get_table_names():
        
        metaData = MetaData()
        table_to_drop = Table(SQLtable, metaData, autoload_with=engine)
        table_to_drop.drop(engine)
        print("Table dropped successfully")

    df.to_sql(SQLtable, con=engine, if_exists='append', index=False)
    print(f"Data updated in table {SQLtable}")
    print(df.head())

def process_excel_data(excelfilepath, engine):
    """
    Process data from the given Excel file and update the SQL tables
    
    Args:
        excelfilepath (str): Path to the Excel file
        engine: The SQLAlchemy engine
    """

    ## Retrive Dataframe from Excel
    df = pd.read_excel(excelfilepath, sheet_name='Overview (USD)')

    ## UIP Stocks
    df_UIP = df[['Name', 'Ticker','Category','Sector','Industry','Country','Market Price', 'Market Cap']]
    FuncUpdateSQLTable(df_UIP, SQLtable='UIPStocks', engine=engine)

    ## Current Portfolio
    df_portfolio = df.loc[df['Remaining']>0]
    df_portfolio = df_portfolio.drop(columns=['Unnamed: 40', 'Unnamed: 41', 'Unnamed: 42'], axis=1)

    FuncUpdateSQLTable(df_portfolio, SQLtable = 'StocksPortfolio', engine=engine)

    ## Watchlist
    df_watchlist = df.loc[df['Amount To Add']!=0]
    df_watchlist = df_watchlist[['Ticker', 'Amount To Add', 'Pessimistic IV', 'Base Case IV', 'Average IV', 'Market Price', 'Buy Point 1', 'Buy Point 2', 'Buy Point 3', 'Buy Point 4']]

    FuncUpdateSQLTable(df_watchlist, SQLtable = 'Watchlist', engine=engine)

    ## Mortgage
    df_mortgage = pd.read_excel(excelfilepath, sheet_name='Resale')
    df_mortgage = df_mortgage.rename(columns={'Unnamed: 29':'Date', 'Unnamed: 30':'Interest', 'Unnamed: 31':'Principal'})
    df_mortgage = df_mortgage[['Date', 'Interest', 'Principal']]
    df_mortgage = df_mortgage.dropna(subset=['Date'])
    FuncUpdateSQLTable(df_mortgage, SQLtable = 'Mortgage', engine=engine)

    ## CPF
    df_cpf = pd.read_excel(excelfilepath, sheet_name='CPF Tracker')
    df_cpf = df_cpf.rename(columns={'CPF Ordinary Account (OA)' : 'CPFOA', 'CPF Special Account (SA)' : 'CPFSA', 'CPF Medisave Account (MA)' : 'CPFMA', 'CPF Retirement Account (RA)' : 'CPFRA'} )
    df_cpf = df_cpf[['Year', 'Month', 'CPFOA', 'CPFSA', 'CPFMA', 'CPFRA']]
    FuncUpdateSQLTable(df_cpf, SQLtable = 'CPF', engine=engine)

    ## Projected Allocation
    df_projected = df.loc[(df['Amount To Add']!=0) | df['Remaining'] > 0]
    df_projected = df_projected[['Ticker','Projected Allocation', 'Allocation']]
    FuncUpdateSQLTable(df_projected, SQLtable = 'ProjectedAllocation', engine=engine)
    
    ## Stocks Transaction
    df_transaction = pd.read_excel(excelfilepath, sheet_name="Purchases (USD)", usecols=range(12))
    FuncUpdateSQLTable(df_transaction, SQLtable = 'StocksTransaction', engine=engine)
    
    print("All data updated successfully")

# # Living Expenses
# csvfilepath = "Transactions_20200104_20240531.csv"

# ## To retrieve the CSV file
# df_expenses = pd.read_csv(csvfilepath, skipinitialspace=True)

# ## To clean up the date columns
# df_expenses = df_expenses.dropna(subset=['Date'])
# df_expenses['Date'] = pd.to_datetime(df_expenses['Date'], dayfirst=True, errors='coerce')
# FuncUpdateSQLTable(df_expenses, SQLtable = 'LivingExpenses')