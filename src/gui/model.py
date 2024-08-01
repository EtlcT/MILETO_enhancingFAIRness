import logging
import os
import pandas as pd

from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.check import CheckSpreadsheet
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate, sqlite2pdf

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class Model:
    def __init__(self):
        self.input_path = None
        self.output_path = None
        self.tmp_data = None
        self.checked_data = None
        self.data = None
    
    def load_spreadsheet(self, filepath):
        try:
            self.tmp_data = pd.read_excel(filepath, sheet_name=None)
        except Exception as e:
            logging.error(f"An error occured reading your file but it si probably not due to the app {str(e)}")
        else:
            return self.tmp_data

    def verify_spreadsheet(self):

        checker = CheckSpreadsheet(self.tmp_data)
        checker.validate_spreadsheet()

        self.checked_data = checker.sheets_dict

    def convert(self, output_name=None):
        
        self.getData()

        if output_name:
            self.data.db_name = output_name
        
        # create sqlite and erd_schema
        createdDb = self.dbCreate()

        # create pdf
        self.pdfCreate(createdDb)

    def getData(self):

        self.data = GetSpreadsheetData(
            filepath=self.input_path,
            checked_data=self.checked_data
        )
    
    def dbCreate(self) -> sqliteCreate:

        sqlite_db = sqliteCreate(
            self.data,
            output_dir=self.output_path
            )
        
        sqlite_db.create_db()
        sqlite_db.insert_data()
        sqlite_db.ddict_schema_create()
        sqlite_db.meta_tables_create()

        return sqlite_db

    def pdfCreate(self, createdDb):

        doc = docCreate(createdDb)
        doc.createPDF()

    def sqlite2pdf(self):
        doc = sqlite2pdf(self.input_path, self.output_path)
        doc.createPDF()