import logging
import os
import pandas as pd

from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.check import CheckSpreadsheet
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class Model:
    def __init__(self):
        self.spreadsheet_path = None
        self.output_path = None
        self.tmp_data = None
        self.checked_data = None
    
    def load_spreadsheet(self, filepath):
        try:
            self.tmp_data = pd.read_excel(filepath, sheet_name=None)
        except Exception as e:
            logging.error(f"An error occured reading your file but it si probably not due to the app {e}")
        else:
            return self.tmp_data

    def verify_spreadsheet(self):

        checker = CheckSpreadsheet(self.tmp_data)
        checker.validate_spreadsheet()

        self.checked_data = checker.sheets_dict

    # TODO split in getData, sqlite create and pdf create
    def convert(self, output_name=None):
    
        self.data = GetSpreadsheetData(
            filepath=self.spreadsheet_path,
            checked_data=self.checked_data
            )
        
        if output_name:
            self.data.db_name = output_name
        
        # create sqlite and erd_schema
        sqlite_db = sqliteCreate(
            self.data,
            output_dir=self.output_path
            )
        
        sqlite_db.create_db()
        sqlite_db.insert_data()
        sqlite_db.ddict_schema_create()
        sqlite_db.meta_tables_create()

        # create pdf
        doc = docCreate(sqlite_db)

        doc.createPDF()