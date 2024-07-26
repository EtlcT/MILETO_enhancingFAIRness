# -*-coding: utf-8 -*-

""" This module reads spreadsheets that respect the defined
template (see README and data/example_template.xls) and
extract data required for conversion into Relationnal DB
"""

import pandas as pd
#import openpyxl # engine used by pandas.read_excel
import re
import sys
import os

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from conf.config import *
from src.utils import file2Blob, bytes_in_df_col
from src.extraction.check import CheckSpreadsheet

class GetSpreadsheetData:
    """
    Class that read a spreadsheet and retrieve required data from it 
    """

    def __init__(self, filepath) -> None:
        self.sheets_dict = self._read_spreadsheet(filepath)
        self.db_name = os.path.splitext(os.path.basename(filepath))[0]
        self.datatables_list = self._get_datatables_list()
        self.tables_info = self._get_tables_info()
        self.compositePK_df = self._get_composite_pk()
        
        self._run_checker()

    def _read_spreadsheet(self, filepath) -> dict:
        """
        return a dictionnary containing as many dataframes as sheets in the original file
        """

        data = pd.read_excel(filepath, sheet_name=None)
        for table_name in data.keys():

            # process_df convert any absolute filepath into 
            # blob of relative file
            self.process_df(data[table_name])

        return data

    #! add file for regex exclusion
    def _regex_exclude_meta(self, text) -> bool:
        """
        return True if text match one of the regex to exclude, false either

        case insensitive regex to keep only data tables
        """
        no_info = re.search(r"(?i)tables_info", text)
        no_meta = re.search(r"(?i)meta\_", text)
        no_DDict = re.search(r"(?i)DDict\_", text)
        no_extra = re.search(r"(?i)extra_sheet\.", text)
        return any([no_DDict, no_meta, no_extra, no_info])


    def _get_datatables_list(self) -> list:
        """
        Return a list containing the name of table that contains effective data

        exclude extra.*, meta.* and DDict.*, tables_info
        """
        datatable_list = list()
        for sheet_name in self.sheets_dict:
            if(self._regex_exclude_meta(sheet_name) == False):
                datatable_list.append(sheet_name)
        return datatable_list


    #! may be deprecated in the future if spreadsheet template is modified
    #? potential future behavior: directly modify sheet_dict[INFO]
    #? and access it instead of creating dedicated Df that is a duplication
    def _get_tables_info(self) -> pd.DataFrame:
        """
        return a dataframe that contain rows from tables_info table
        where 'Table' belong to data table list (ie self.datatables_list)
        """

        tables_info = self.sheets_dict[INFO][self.sheets_dict[INFO][INFO_ATT["table"]]
                                        .isin(self.datatables_list)] \
                                        .iloc[:,:5]
        # add type info 
        tables_info_wt = self._add_attr_type(tables_info)

        return tables_info_wt

    def _get_composite_pk(self) -> pd.DataFrame:
        """
        Return a Dataframe containing table name and composite key fields
        """
        composite_pk_df = pd.DataFrame(columns=['Table', 'pk_fields'])
        group_by_table = self.tables_info.groupby(by=INFO_ATT["table"])

        for table_name, table_info in group_by_table:
            pk_attr = table_info[table_info[INFO_ATT['isPK']]=='Y'][INFO_ATT['attribute']].tolist()
            if len(pk_attr)>1:
                new_row = pd.DataFrame([{'Table': table_name,'pk_fields': pk_attr}])
                composite_pk_df = pd.concat(
                    [composite_pk_df, new_row],
                    ignore_index=True
                )
                
        return composite_pk_df
    
    # TODO CHECK
    def _add_attr_type(self, tables_info) -> pd.DataFrame:
        """Auto detect attr types based on dataframe content
        store the type info in new column 'type' in tables_info

        return tables_info with type info for each attribute
        """

        tables_info['type'] = pd.Series()

        for table in self.datatables_list:
            for attr, pd_type in self.sheets_dict[table].dtypes.items():

                if re.search('int', str(pd_type)) != None:
                    # attribute type is an integer
                    table_value = tables_info[INFO_ATT['table']] == table
                    attr_value = tables_info[INFO_ATT['attribute']] == attr
                    # access row in tables_info and change type value
                    tables_info.loc[(table_value & attr_value), 'type'] = 'INTEGER'
                
                elif re.search('float', str(pd_type)) != None:
                    # attribute type is a float
                    table_value = tables_info[INFO_ATT['table']] == table
                    attr_value = tables_info[INFO_ATT['attribute']] == attr
                    # access row in tables_info and change type value
                    tables_info.loc[(table_value & attr_value), 'type'] = "REAL"

                else:
                    table_value = tables_info[INFO_ATT['table']] == table
                    attr_value = tables_info[INFO_ATT['attribute']] == attr

                    if(bytes_in_df_col(self.sheets_dict[table][attr])):
                        tables_info.loc[(table_value & attr_value), 'type'] = "BLOB"
                        # force type to be str (prevent bug at insertion time)
                        self.sheets_dict[table][attr] = (
                            self.sheets_dict[table][attr].astype(bytes)
                        )
                    else:
                        # access row in tables_info and change type value
                        tables_info.loc[(table_value & attr_value), 'type'] = "TEXT"
                        # force type to be str (prevent bug at insertion time)
                        self.sheets_dict[table][attr] = (
                            self.sheets_dict[table][attr].astype(str)
                        )
   
        return tables_info
    
    def _run_checker(self):
        checker = CheckSpreadsheet(self.sheets_dict, self.tables_info)
        checker.validate_spreadsheet()

    # TODO CHECK
    @staticmethod
    def process_df(table: pd.DataFrame) -> None:
        """
        if a column contain filepath, relative file is accessed and
        converted to blob
        """

        for col in table.columns:
            table[col] = table[col].apply(
                lambda x: file2Blob(x) if os.path.isabs(str(x).replace('\\','\\')) else x
            )

        return