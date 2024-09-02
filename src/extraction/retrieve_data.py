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
from PIL import Image

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from conf.config import *
from src.utils.utils_extraction import get_datatables_list, bytes_in_df_col, img2Blob

class GetSpreadsheetData:
    """
    Class that retrieve and process data that has been retrieved from
    pd.read_excel and already checked by CheckSpreadsheet class
    """

    def __init__(self, filepath, checked_data) -> None:
        self.db_name = os.path.splitext(os.path.basename(filepath))[0]
        self.file_dir = os.path.dirname(filepath)
        self.datatables_list = get_datatables_list(checked_data)
        self.sheets_dict = self.process_img_column(checked_data)
        self.tables_info = self._get_tables_info()
        self.compositePK_df = self._get_composite_pk()
        
    def process_img_column(self, checked_data):
        """Return checked data after convert image path to blob
        if some column match the IMG_COL_REGEX see conf/config

        If provided file path does not exist or is not accessible
        initial entry is cleared
        """
        for table_name in checked_data.keys():
            if table_name in self.datatables_list:
                # iterate through data tables
                for col in checked_data[table_name].columns:
                    # for each column
                    for regex in IMG_COL_REGEX:
                        if re.search(regex, col):
                            # column match regex
                            checked_data[table_name][col] = checked_data[table_name][col].map(
                                lambda x: img2Blob(x, self.file_dir) if self.is_image(x) else ""
                            )
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
                                        .iloc[:,:6]
        # add type info 
        tables_info_wt = self._add_attr_type(tables_info)

        return tables_info_wt

    def _get_composite_pk(self) -> pd.DataFrame:
        """
        Return a Dataframe containing table name and composite key fields
        """
        composite_pk_df = pd.DataFrame(columns=['table', 'pk_fields'])
        group_by_table = self.tables_info.groupby(by=INFO_ATT["table"])

        for table_name, table_info in group_by_table:
            pk_attr = table_info[table_info[INFO_ATT['isPK']]=='Y'][INFO_ATT['attribute']].tolist()
            if len(pk_attr)>1:
                new_row = pd.DataFrame([{'table': table_name,'pk_fields': pk_attr}])
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
    
    def is_image(self, var):
        """Return True if var if an existing path to an image False if not"""

        try:
            if os.path.isfile(os.path.abspath(var)):
                file_path = os.path.abspath(var)
            elif os.path.isfile(os.path.abspath(os.path.join(self.file_dir, "images", var))):
                file_path = os.path.abspath(os.path.join(self.file_dir, "images", var))
            
            if re.search(".svg$", file_path):
                return True
            else:
                im = Image.open(file_path)
                # if no exception is raised, it's a valid image
                return True
        except Exception as e:
            return False