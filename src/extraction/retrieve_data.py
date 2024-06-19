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

from src.extraction.utils import check_uniqueness

class GetSpreadsheetData:
    """
    Class that read a spreadsheet and retrieve required data from it 
    """

    def __init__(self, filepath) -> None:
        self.sheets_dict = self._read_spreadsheet(filepath)
        self.db_name = self._get_dbname()
        self.datatables_list = self._get_datatables_list()
        self.table_structure = self._get_table_structure()
        self.compositePK_df = self._get_composite_pk()
    
    def _read_spreadsheet(self, filepath) -> dict:
        """
        return a dictionnary containing as many dataframes as sheets in the original file
        """
        
        return pd.read_excel(filepath, sheet_name=None)
    
    #?
    def _regex_exclude_meta(self, text) -> bool:
        """
        return True if text match one of the regex to exclude, false either

        case insensitive regex to keep only data tables
        """
        no_keys = re.search("(?i)^keys$", text)
        no_meta = re.search("(?i)meta\.", text)
        no_extra = re.search("(?i)extra_sheet\.", text)
        return any([no_keys, no_meta, no_extra])

    #?
    def _get_datatables_list(self) -> list:
        """
        Return a list containing the name of table that contains effective data

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
    #?
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

    #?
    def _get_composite_pk(self) -> pd.DataFrame:
        """
        Return a Dataframe containing table name and composite key fields
        """
        composite_pk_df = pd.DataFrame(columns=['Table', 'pk_fields'])
        group_by_table = self.table_structure.groupby(by='Table')

        for table_name, table_info in group_by_table:
            pk_attr = table_info[table_info['isPK']=='Y']['Attribute'].tolist()
            if len(pk_attr)>1:
                new_row = pd.DataFrame([{'Table': table_name,'pk_fields': pk_attr}])
                composite_pk_df = pd.concat(
                    [composite_pk_df, new_row],
                    ignore_index=True
                )
                
        return composite_pk_df
                
    #?
    def check_pk_uniqueness(self) -> None:
        """
        Raise assertion error if fields defined as Primary Key does not
        respect uniqueness criteria
        """
        pk_constraint = self.table_structure[self.table_structure['isPK'] == 'Y'][['Table','Attribute']]
        pk_groupedby_table = pk_constraint.groupby(by='Table')
        for table_name, pk_info in pk_groupedby_table:
            pk_info = pk_info['Attribute'].tolist()

            assert check_uniqueness(field=pk_info, table=self.sheets_dict[table_name]),\
                    f"invalid primary key constraint {pk_info} for table {table_name}\n\
                    Primary must be unique"
            
        return
    
    def check_FK_existence_and_uniqueness(self) -> None:
        """
        Raise assertion error if FK is not present in Reference Table
        """

        isFK_condition = self.table_structure['isFK']=='Y'
        fk_constraint = self.table_structure[isFK_condition]['Table','Attribute','ReferenceTable']
        fk_by_table_and_ref = fk_constraint.groupby(by=['Table','ReferenceTable'])

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
                exist_in_ref = (col in self.sheets_dict[ref_table_name].columns
                                for col in fk_info['Attribute'])
                
                assert all(exist_in_ref),\
                    f"invalid Foreign key {fk_info['Attribute']} for {table_name}\n\
                        all attributes must be present in {ref_table_name}"
                
                assert check_uniqueness(
                    field=fk_info['Attribute'],
                    table=self.sheets_dict[ref_table_name]
                ),\
                    f"invalid Foreign key {fk_info['Attribute']} for {table_name}\n\
                        all attributes must be present in {ref_table_name}"

        return
    
    #?
    def check_pk_defined(self) -> None:
        """Raise AssertionError if a table has no Primary Key defined"""

        for table, table_info in self.table_structure.groupby(by='Table'):
            assert 'Y' in table_info['isPK'].values, f"Table {table} has no Primary Key defined"
        
        return