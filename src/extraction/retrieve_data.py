# -*-coding: utf-8 -*-

""" This module reads spreadsheets that respect the defined
template (see README and data/example_template.xls) and
extract data required for conversion into Relationnal DB
"""

import pandas as pd
#import openpyxl # engine used by pandas.read_excel
import re

class GetSpreadsheetData:
    """
    Class that read a spreadsheet and retrieve required data from it 
    """

    def __init__(self, filepath) -> None:
        self.sheets_dict = self._read_spreadsheet(filepath)
        self.db_name = self._get_dbname()
        self.datatables_list = self._get_datatables_list()
        self.table_structure = self._get_table_structure()
    
    def _read_spreadsheet(self, filepath) -> dict:
        """
        return a dictionnary containing as many dataframes as sheets in the original file
        """
        return pd.read_excel(filepath, sheet_name=None)
    
    def _regex_exclude_meta(self, text) -> bool:
        """
        return True if text match one of the regex to exclude, false either

        case insensitive regex to keep only data tables
        """
        no_keys = re.search("(?i)^keys$", text)
        no_meta = re.search("(?i)meta\.", text)
        no_extra = re.search("(?i)extra_sheet\.", text)
        return any([no_keys, no_meta, no_extra])

    def _get_datatables_list(self) -> list:
        """
        return a list containing the name of table that contains effective data

        exclude KEYS, meta.* and DDict.*
        """
        datatable_list = list()
        for sheet_name in self.sheets_dict:
            if(self._regex_exclude_meta(sheet_name) == False):
                datatable_list.append(sheet_name)
        return datatable_list

    #! may be deprecated in the future if spreadsheet template is modified
    #? potential future behavior: directly modify sheet_dict['KEYS']
    #? and access it instead of creating dedicated Df that is a duplication
    def _get_table_structure(self) -> pd.DataFrame:
        """
        return a dataframe that contain rows from KEYS table
        where 'Table' belong to data table list (ie self.datatables_list)
        """
        
        return self.sheets_dict['KEYS'][self.sheets_dict['KEYS']['Table']
                                        .isin(self.datatables_list)] \
                                        .iloc[:,:5]

    def _get_dbname(self) -> str:
        """
        return the database name as specified in the spreadsheet meta.References sheet
        """
        db_name = self.sheets_dict['meta.REFERENCES']\
            [self.sheets_dict['meta.REFERENCES']['key'] == 'DBfileName']\
            ['value'].values[0]

        # remove unwanted character from file name
        db_name = re.sub("[$#%&?!+\-,;\.:'\"\/\\[\]{}|\s]", "", db_name)
        return db_name

    def check_PK_uniqness(self) -> bool:
        """
        check that fields sets are PK contain unique value
        """

        pk_constraint = self.table_structure[self.table_structure['isPK'] == 'Y'][['Table','Attribute']]
        pk_groupedby_table = pk_constraint.groupby(by='Table')
        for table_name, pk_info in pk_groupedby_table:
            nb_pk = len(pk_info.tolist())
            # check if it is a composite PK or not
            if nb_pk == 1: 
                assert self.sheets_dict[table_name][pk_info.loc[0]].is_unique == True,\
                    f"invalid primary key constraint {pk_info.iloc[0]} for table {table_name}\
                    \nPK should be unique"
                
            else: # this is a composite PK
                count_combination = (
                    self.sheets_dict[table_name]
                    .groupby(by=[pk_info.iloc[i] for i in range(nb_pk)])
                    .size()
                    .reset_index(name='count')
                )

                assert (count_combination['count']==1).all() == True,\
                f"invalid primary key constraint {[pk_info.iloc[i] for i in range(nb_pk)]} for table {table_name}\
                \nPK should be unique"

        return

    #! not used anymore, see _get_table_structure instead    
    def _get_keys_df(self) -> pd.DataFrame:
        """
        return a dataframe that contain rows from KEYS table
        where either Primary Key OR Foreign Key is not null
        """
        keys_df = self.sheets_dict['KEYS'][self.sheets_dict['KEYS']['isPK'].notna()
                                            | self.sheets_dict['KEYS']['isFK'].notna()].iloc[:,:5]
        
        return keys_df.reset_index(drop=True)
    
    

