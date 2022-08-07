# For querying the database.
import os
import sqlite3

# For number storage and manipulation.
import pandas as pd

# Database utilities.
from Database_Writer.database_utils import DatabaseUtilities

# Directory where you want the database files to be stored. 
db_directory = "Your path here\\ROIC\\Database_Files"


class AssetDatabase(DatabaseUtilities):
    def __init__(self, ticker: str):
        # Establish connection to the database we want.
        self.conn = sqlite3.connect(f"{db_directory}\\{ticker.upper()}.db")
        # Create cursor object
        self.cur = self.conn.cursor()
        self.db_filename = ticker + ".db"
        super().__init__(self.conn)

    '-------------------------------------------------------'
    def create_table_from_dataframe(self, df: pd.DataFrame, table_type: str):
        '''
        - Takes a pandas dataframe and will create a table based on the data contained within the dataframe.
        :param df: Dataframe to insert.
        :param table_type: Determine what type of table to create.
        :return: None
        '''
        # Possible table types
        #----------------
        # summary
        # income_statement
        # balance_sheet
        # cash_flow
        exists = self.check_if_table_exists(table_name=table_type)
        # If there is not already data in this file.
        if not exists:
            # Convert dataframe to sqlite table.
            df.to_sql(table_type,self.conn,if_exists="replace")



