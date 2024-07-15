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
from src.utils import check_uniqueness, file2Blob, bytes_in_df_col

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


    def check_pk_uniqueness(self) -> None:
        """
        Raise assertion error if fields defined as Primary Key does not
        respect uniqueness criteria
        """
        pk_constraint = self.tables_info[self.tables_info[INFO_ATT['isPK']] == 'Y'][[INFO_ATT['table'],INFO_ATT['attribute']]]
        pk_groupedby_table = pk_constraint.groupby(by=INFO_ATT['table'])
        for table_name, pk_info in pk_groupedby_table:
            pk_info = pk_info[INFO_ATT['attribute']].tolist()

            assert check_uniqueness(
                fields=pk_info,
                table=self.sheets_dict[table_name]
            ), (
                f"invalid primary key constraint {pk_info} for table {table_name}\n"
                "Primary must be unique"
            )
            
        return
    

    def check_FK_existence_and_uniqueness(self) -> None:
        """
        Raise assertion error if FK is not present in Reference Table or
        if the reference attribute does not respect unicity 
        """

        isFK_condition = self.tables_info[INFO_ATT['isFK']]=='Y'
        fk_by_table_and_ref = (
            self.tables_info[isFK_condition][[
                INFO_ATT["table"],
                INFO_ATT['attribute'],
                INFO_ATT['refTable']
            ]]
            .groupby(by=[INFO_ATT["table"],INFO_ATT['refTable']])
        )

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
                exist_in_ref = (col in self.sheets_dict[ref_table_name].columns
                                for col in fk_info[INFO_ATT['attribute']])
                
                # check that the attribute exist in reference table
                assert all(exist_in_ref),(
                    f"invalid Foreign key {fk_info[INFO_ATT['attribute']].tolist()} for {table_name}\n"
                    f"all attributes must be present in {ref_table_name}"
                )

                assert check_uniqueness(
                    fields=fk_info['attribute'].tolist(),
                    table=self.sheets_dict[ref_table_name]
                ), (
                    f"invalid Foreign key {fk_info['attribute'].tolist()} for {table_name}\n"
                    f"the reference attribute in {ref_table_name} should be unique"
                )

        return
    

    def check_pk_defined(self) -> None:
        """Raise AssertionError if a table has no Primary Key defined"""

        for table, table_info in self.tables_info.groupby(by=INFO_ATT["table"]):
            assert 'Y' in table_info[INFO_ATT['isPK']].values, f"Table {table} has no Primary Key defined"
        
        return
    

    def check_fk_get_ref(self) -> None:
        """
        Raise AssertionError if a field is defined as FK 
        but has empty ReferenceTable field
        """

        isFK_condition = self.tables_info[INFO_ATT['isFK']]=='Y'
        fk_constraint = self.tables_info[isFK_condition]

        assert not fk_constraint[INFO_ATT['refTable']].isna().any(), (
            "Every FK should have a reference table defined"
            f"{fk_constraint[fk_constraint[INFO_ATT['refTable']].isna()==True]}"
        )
    
    def check_no_shared_name(self) -> None:
        """
        Raise AssertionError if fields that belong to different 
        tables have the same name, except for foreign keys (for which
        it could be normal to share the same name as their reference)
        """

        notFK_condition = self.tables_info[INFO_ATT['isFK']].isna()
        attr_no_FK = self.tables_info[notFK_condition]

        assert attr_no_FK[INFO_ATT['attribute']].is_unique, (
            "Except for Foreign keys, different attributes should not"
            "have the same names"
        )

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