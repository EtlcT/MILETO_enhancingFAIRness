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
from src.utils.utils_extraction import get_datatables_list
from src.utils.utils import file2Blob, bytes_in_df_col

class GetSpreadsheetData:
    """
    Class that retrieve and process data that has been retrieved from
    pd.read_excel and already checked by CheckSpreadsheet class
    """

    def __init__(self, filepath, checked_data) -> None:
        self.datatables_list = get_datatables_list(checked_data)
        self.sheets_dict = self._process_data(checked_data)
        self.db_name = os.path.splitext(os.path.basename(filepath))[0]
        self.tables_info = self._get_tables_info()
        self.compositePK_df = self._get_composite_pk()
        

    def _process_data(self, checked_data) -> dict:
        """
        return a dictionnary containing as many dataframes as sheets in the original file
        and convert path_file into blob of the file
        """

        for table_name in checked_data.keys():
            if table_name not in self.datatables_list:
                # process_df convert any absolute filepath into 
                # blob of relative file
                self.process_df(checked_data[table_name])

        return checked_data

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