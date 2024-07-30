import logging
import os
import pandas as pd

from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.check import CheckSpreadsheet
from src.dbcreate.dbcreate import sqliteCreate

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class Model:
    def __init__(self):
        self.spreadsheet_path = None
        self.output_path = None
        self.tmp_data = None
        self.data = None
    
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

    def convert_all(self):

        self.data = GetSpreadsheetData(self.spreadsheet_path)