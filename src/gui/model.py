import logging
import os

from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class Model:
    def __init__(self):
        self.spreadsheet_path = None
        self.output_path = None
        self.data = None
    
    def verify_spreadsheet(self):
        self.data = GetSpreadsheetData(filepath=self.spreadsheet_path)
