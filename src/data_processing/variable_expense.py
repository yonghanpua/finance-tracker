import pandas as pd
import numpy as np
# import pyodbc as odbc
import calendar
import xlwings as xw
from src.utils.log_result import logResult
from src.db.connect_db import connectDB
from config.settings import EXCEL_PATH, LOG_PATH

# File Paths
excelfilepath = EXCEL_PATH
log_path = LOG_PATH
# csvfilepath = r"data/Transactions 01 Jan 2024 - 31 Dec 2024.csv"

# Function to map month numbers to month names
def month_number_to_name(month_number):
    
    return calendar.month_name[month_number]

# Convert Date to DateTime
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']


# Function to process the variable expenses
def ProcessVarExp(csvfilepath):
    """
    Process variable expenses from a CSV file and update the Excel workbook

    Args:
        csvfilepath (str): Path to the input CSV file
        excelfilepath(str): Path to the Excel workbook
        log_path (str): Path to the log file
    
    Returns:
        None
    """
    # Runs a connection to the database
    # engine = connectDB()

    try:
        # Load and filter new data from CSV
        df = load_and_clean_csv(csvfilepath)
        
        # Pivot new data for monthly expenses
        df_grouped = create_monthly_pivot(df)
        
        # Load existing data from Excel
        df_existing = load_existing_data(excelfilepath)
        
        # Detect new or changed data and update
        df_pivot_final = detect_changes_and_update(df_existing, df_grouped)
        
        # Write updated data back to Excel
        write_to_excel(excelfilepath, df_pivot_final)
        
        # Log the update
        logResult(log_path, "Personal Portfolio Updated Successfully.")
        
    except Exception as e:
        logResult(log_path, f"Error processing variable expenses: {e}")
        raise

# Load nad clean new data from CSV
def load_and_clean_csv(csvfilepath):
    df = pd.read_csv(csvfilepath, skipinitialspace=True)
    df = df.dropna(subset=['Date']) # Drop rows without a Date
    df = df[df['Category'].isin(['Food & Drinks', 'Groceries', 'Gifts & Charity', 'Shopping', 'Entertainment', 'Enrichment', 'Personal Care', 'Healthcare', 'Transportation', 'General', 'Vacation'])]

  
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year.fillna(0).astype(int)
    df['MonthNum'] = df['Date'].dt.month.fillna(0).astype(int)
    df['Month'] = df['MonthNum'].apply(month_number_to_name)
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
    df['Amount'] = df['Amount'].abs()
    return df

# Create a pivot table from the new data
def create_monthly_pivot(df):
    df_grouped = df.groupby(['Year', 'Month', 'Category'], observed=False)['Amount'].sum().reset_index()
    return df_grouped[df_grouped["Amount"] > 0]


# Load existing data from Excel and convert to DataFrame
def load_existing_data(excelfilepath):
    # Load existing data from Excel and convert into DataFrame
    wb = xw.Book(excelfilepath)
    sheet = wb.sheets["Living Expenses Summary"]
    used_range = sheet.used_range.value # Returns the data as a list of lists
    df_existing = pd.DataFrame(used_range[1:], columns=used_range[0]) # Skip the header row in the data (hence [1:]) 
    df_existing = df_existing.dropna(how="all").reset_index(drop=True)
    df_existing['Year'] = df_existing['Year'].astype(int)
    
    df_existing_unpivot = pd.melt(df_existing, id_vars=["Year", "Category"], var_name="Month", value_name="Amount")
    return df_existing_unpivot.reset_index(drop=True)

# Detect new or changed data and update existing DataFrame
def detect_changes_and_update(df_existing_unpivot, df_grouped):
    """
    Detects new or changed data and updates the existing DataFrame

    Args:
        df_existing_unpivot (DataFrame): Unpivoted existing data from Excel
        df_grouped (DataFrame): Grouped and pivoted new data

    Returns:
        DataFrame: Final pivoted DataFrame with updates applied
    """
    # merge data to detect changes
    df_combined = pd.merge(
        df_existing_unpivot,
        df_grouped,
        on=["Year", "Month", "Category"],
        how="outer",
        suffixes=("_existing", "_new")
    )

    # Identify new or updated entries
    df_combined["is_updated"] = df_combined["Amount_existing"] != df_combined["Amount_new"]
    
    # Select rows where updates are present or existing data is missing
    # df_changes = df_combined[df_combined["is_updated"] | df_combined["Amount_existing"].isnull()] -- Updated 20250125
    df_changes = df_combined[df_combined["is_updated"] | df_combined["Amount_existing"].isnull()].copy()
    
    # Safely assign the updated 'Amount' column
    # df_changes["Amount"] = df_changes["Amount_new"].fillna(df_changes["Amount_existing"]) -- Updated 20250125
    df_changes.loc[:, "Amount"] = df_changes["Amount_new"].fillna(df_changes["Amount_existing"])

    # Keep only the necessary columns and format data
    df_final = df_changes[['Year', 'Month', 'Category', 'Amount']].reset_index(drop=True)
    df_final['Month'] = pd.Categorical(df_final['Month'], categories=month_order, ordered=True)
    df_final = df_final.groupby(['Year', 'Month', 'Category'], observed=False)['Amount'].sum().reset_index()
    df_pivot_final = df_final.pivot_table(index=['Year', 'Category'], columns='Month', values='Amount', aggfunc='sum', fill_value=0, observed=False)    
    return df_pivot_final

# Write updated data to Excel and set Accounting format
def write_to_excel(excelfilepath, df_pivot_final):
    wb = xw.Book(excelfilepath)
    sheet = wb.sheets["Living Expenses Summary"]
    
    # Write DataFrame to Excel
    sheet.range('A1').value = df_pivot_final
    
    # Set Accounting format for the data range
    last_row = sheet.range("A1").expand("table").last_cell.row
    last_column = sheet.range("A1").expand("table").last_cell.column
    data_range = sheet.range((2,3), (last_row, last_column)) # Adjust to excluse headers
    data_range.number_format = '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
        
    # # Save workbook
    # wb.save()
    
## Additional Codes
# grouped_df.to_excel(excelfilepath, sheet_name='Living Expense Summary', index=False)
# FuncUpdateSQLTable(df=df_grouped,SQLtable='MonthlyExpense')

