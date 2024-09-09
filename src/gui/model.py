import logging
import os
import pandas as pd
import numpy as np

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
    
    def create_missing_metatable(self):
        """Create metadata tables if not exist return list of
        missing metadata table"""

        meta_generator = GenerateMeta(self.tmp_data)
        missing_tables = meta_generator.create_metatable()
        return missing_tables
    
    def header_change(self, table, old_value, new_value):
        """On changes in header/attribute, report change everywhere else
        in metadata tables and relative fields.
        """
        self.upt_header(table, old_value, new_value)
        self.upt_meta_attr(table, old_value, new_value)
        self.upt_ref(table, old_value, new_value)

    def upt_header(self, table, old_value, new_value):
        """Update column value of datatable and modify metadata tables
        accordingly
        """
        # rename previous column
        self.tmp_data[table].rename(columns={old_value:new_value}, inplace=True)

    def upt_meta_attr(self, table, old_value, new_value):
        """On changes in header, update metadata tables"""
        
        # update tables_info
        self.tmp_data[INFO].loc[
            (self.tmp_data[INFO][INFO_ATT["table"]] ==  table) &
            (self.tmp_data[INFO][INFO_ATT["attribute"]] ==  old_value),
            [INFO_ATT["attribute"]]
        ] = new_value

        # update datadict_attribute
        self.tmp_data[DDICT_A].loc[
            (self.tmp_data[DDICT_A]["attribute"] ==  old_value),
            [DDICT_A_ATT["attribute"]]
        ] = new_value

    def upt_ref(self, table, old_value, new_value):
        """On changes in header, check if attribute is a reference
        find potential parent or child table and update modified attribute
        inside
        """

        # retrieve parent table of the attribute if it has a referenceTable
        parent_tables = self.tmp_data[INFO].loc[
            (self.tmp_data[INFO][INFO_ATT["table"]] ==  table) &
            (self.tmp_data[INFO][INFO_ATT["attribute"]] ==  new_value),
            INFO_ATT["refTable"]
        ].values
        
        # retrieve child table of the attribute if it is a reference
        child_tables = self.tmp_data[INFO].loc[
            (self.tmp_data[INFO][INFO_ATT["refTable"]] ==  table) &
            (self.tmp_data[INFO][INFO_ATT["attribute"]] ==  old_value),
            INFO_ATT["table"]
        ].values

        for parent_table in parent_tables:
            if parent_table != "":
                if old_value in self.tmp_data[parent_table].columns:
                    self.upt_header(parent_table, old_value, new_value)
                    self.upt_meta_attr(parent_table, old_value, new_value)
        for child_table in child_tables:
            if child_table != "":
                if old_value in self.tmp_data[child_table].columns:
                    self.upt_header(child_table, old_value, new_value)
                    self.upt_meta_attr(child_table, old_value, new_value)
        
    def upt_cell(self, table, row, col, new_value):
        """Update cell content of metadata table"""
        
        self.tmp_data[table].iloc[row, col] = new_value
        return

    def load_spreadsheet(self, filepath):
        try:
            self.tmp_data = pd.read_excel(filepath, sheet_name=None, keep_default_na=False)
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