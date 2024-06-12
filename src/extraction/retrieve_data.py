# -*-coding: utf-8 -*-

""" This module reads spreadsheets that respect the defined
template (see README and data/example_template.xls) and
extract data required for conversion into Relationnal DB
"""

import pandas as pd
import openpyxl # engine used by pandas.read_excel
import re

class GetSpreadsheetData:
    """
    Class that read a spreadsheet and retrieve required data from it 
    """

    def __init__(self, filename) -> None:
        self.sheets_dict = self._read_spreadsheet(filename)
        self.dbname = self.get_dbname()
    
    def _read_spreadsheet(self) -> dict:
        """
        return a dictionnary containing as many dataframes as sheets in the original file
        """
        return pd.read_excel(self.filename, sheet_name=None)
    
    def _regex_exclude_meta(self, text) -> bool:
        """
        return True if text match one of the regex to exclude, false either

        case insensitive regex to keep only data tables
        """
        no_keys = re.search("(?i)^keys$", text)
        no_meta = re.search("(?i)meta\.", text)
        no_extra = re.search("(?i)extra_sheet\.", text)
        return any(no_keys, no_meta, no_extra)


    def get_datatables_list(self) -> list:
        """
        return a list containing the name of table that contains effective data

        exclude KEYS, meta.* and DDict.*
        """
        datatable_list = list()
        for sheet_name in self.sheets_dict:
            if(self._regex_exclude_meta(sheet_name) == False):
                datatable_list.append(sheet_name)
        
    def _get_keys_df(self) -> pd.DataFrame:
        """
        return a dataframe that contain rows from KEYS table
        where either Primary Key OR Foreign Key is not null
        """

        return self.sheets_dict['KEYS'][self.sheets_dict['KEYS']['isPK'].notna()
                                            | self.sheets_dict['KEYS']['isFK'].notna()].iloc[:,:5]
    
    def get_dbname(self) -> str:
        """
        return the database name as specified in the spreadsheet meta.References sheet
        """

        return self.sheets_dict['meta.REFERENCES'][self.sheets_dict['meta.REFERENCES']['key'] == 'DBfileName']['value'].values[0]

