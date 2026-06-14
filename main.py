# # from src.data_processing.variable_expense import ProcessVarExp

# # csvfilepath = r"data/Transactions 01 Jan 2024 - 31 Dec 2024.csv"

# # ProcessVarExp(csvfilepath)

# from src.db.connect_db import connectDB
# from src.services.file_watcher import Watcher
# from src.data_processing.stock_portfolio import *

# ## Excel Path


# def main():
    
#     # Path to the Excel file
#     excelfilepath = r"C:/Users/yongh/OneDrive/01 Personal/03 Finance/01 Personal Portfolio/Personal Portfolio.xlsm"
    
#     # Connect to the SQL database
#     engine = connectDB()
    
#     # Process and update data
#     process_excel_data(excelfilepath, engine)
    
#     # Create an instance of the Watcher class
#     watcher = Watcher()
    
#     # Run the file watcher
#     watcher.run()

# if __name__ == '__main__':
#     main()

from src.services.file_watcher import Watcher

def main():
    # Create an instance of the Watcher class
    watcher = Watcher()
    
    # Run the file watcher
    watcher.run()

if __name__ == '__main__':
    main()
    
    
