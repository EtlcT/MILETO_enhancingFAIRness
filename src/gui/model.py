import logging
import os
import pandas as pd

from conf.config import *
from src.extraction.create_metadata import GenerateMeta
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
        self.change_log = None
    
    ## could retrieve data from tables_infos
    # if changes are allowed only after first metadata check
    def create_logs(self):
        """Create a dataframe to store changes about headers (field)"""
        data = {"table": [], "init_attr":[], "former_attr": [], "curr_attr": []}
        for table_name, table in self.tmp_data.items():
            for column in table.columns:
                data["table"].append(table_name)
                data["init_attr"].append(column)
                data["former_attr"].append(column)
                data["curr_attr"].append(column)
        
        self.change_log = pd.DataFrame(data)

        return
    
    def create_metatable(self):
        """Create metadata tables if not exist"""

        meta_generator = GenerateMeta(self.tmp_data)
        missing_tables = []
        for metatable in META_TABLES:
            if metatable not in list(self.tmp_data.keys()):
                missing_tables.append(metatable)
                if metatable == METAREF:
                    meta_generator.generate_meta_ref()
                elif metatable == INFO:
                    meta_generator.generate_tables_info()
                elif metatable == DDICT_T:
                    meta_generator.generate_ddict_tables()
                elif metatable == DDICT_A:
                    meta_generator.generate_ddict_attr()
                elif metatable == METAEXTRA:
                    meta_generator.generate_meta_extra()
        return missing_tables


    def upt_change_log(self, table, old_value, new_value) -> None:
        """update change_log to keep track of fields name changes"""
        self.change_log.loc[
            (self.change_log["table"] == table) &
            (self.change_log["curr_attr"] == old_value ),
            ["former_attr", "curr_attr"]
        ] = [old_value, new_value]

        return
    
    def upt_cell(self, table, row, col, new_value):
        """Update cell content of metadata table"""
        
        self.tmp_data[table].iloc[row, col] = new_value
        return

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