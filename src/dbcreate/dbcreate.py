# -*-coding: utf-8 -*-

""" This module does the creation of sqlite database
from data tables dataframes and Keys description.
"""

import sys
import os

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import argparse
import sqlite3
import pandas as pd
from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.utils import checks_pipeline

class sqliteCreate():
    """
    Class that create a sqlite file based on data from extraction module
    """

    def __init__(self, getData: object) -> None:
        assert isinstance(getData, GetSpreadsheetData)
        self.data = getData

    def create_db(self) -> None:
        """
        Iterate through tables_structure dataframe to create table
        with both PK and FK constraints

        This function create a sqlite file
        """

        filename = f"{self.data.db_name}.sqlite"
        conn = sqlite3.connect(database=filename)
        
        group_by_table = self.data.tables_structure.groupby(by='Table')
        for table_name, table_info in group_by_table:

            column_list = table_info['Attribute'].tolist()
            pk_attr = table_info[table_info['isPK']=='Y']['Attribute']

            query = self._add_PK_constraint(table_name, column_list, pk_attr)

            isFK_condition = ~table_info['isFK'].isna()
            group_by_table_ref = (
                table_info[isFK_condition]
                .groupby('ReferenceTable')
            )

            for ref_table_name, ref_info in group_by_table_ref[['Attribute', 'ReferenceTable']]:

                fk_statement = self._add_FK_constraint(
                    ref_table_name=ref_table_name,
                    fk_attribute=ref_info['Attribute'].tolist()
                )
                query += fk_statement
            
            query += ")"
            print(query)
            conn.execute(query)

        conn.close()

    def insert_data(self) -> None:
        """
        Insert data into database
        """

        filename = f"{self.data.db_name}.sqlite"
        conn = sqlite3.connect(filename)
        for table in self.data.datatables_list:
            self.data.sheets_dict[table].to_sql(name=table,
                                           con=conn,
                                           if_exists='append',
                                           index=False
                                           )
        return


    def _add_PK_constraint(self, table_name: str, column_list: list, pk_attribute: list) -> str:
        """
        return a valid sql query for sqlite database CREATE TABLE <> 
        with primary key constraint
        """

        # check if it is a composite Primary KEY
        if len(pk_attribute)>1:
            query = f"CREATE TABLE {table_name} ({', '.join(column_list)}"
            pk_statement = f", PRIMARY KEY ({', '.join([PK_field_name for PK_field_name in pk_attribute])})"
            query += pk_statement

        else: # if it is not a composite PK
            column_list = list(map(lambda x: x.replace(pk_attribute.iloc[0], f'{pk_attribute.iloc[0]} PRIMARY KEY'), column_list)) # map to add 'PRIMARY KEY' as a constrain after the name
            query = f"CREATE TABLE {table_name} ({', '.join(column_list)}"

        return query


    def _add_FK_constraint(self, ref_table_name: str, fk_attribute: list) -> str:
        """
        Return a part of sql statement relative to Foreign keys constraint
        FOREIGN KEYS (field_name) REFERENCES ref_table_name(field_name)
        
        inputs:
            ref_table_name: name of the reference table
            fk_attribute: list of fields defined as foreign keys

        !!WARNING!! field name must be the same in child and parent table
        """
        fk_statement = str()
        fk_statement += (
            f", FOREIGN KEY ({(', ').join(fk_attribute)}) "
            f"REFERENCES {ref_table_name}({(', ').join(fk_attribute)})"
        )
        
        return fk_statement


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to the spreadsheet you want to convert")
    args = parser.parse_args()
    
    getData = GetSpreadsheetData(filepath=args.filepath)

    check_funcs_list = [
        getData.check_pk_defined,
        getData.check_pk_uniqueness,
        getData.check_fk_get_ref,
        getData.check_FK_existence_and_uniqueness
    ]
    checks_pipeline(check_funcs_list)

    dbCreate = sqliteCreate(getData)
    dbCreate.create_db()
    dbCreate.insert_data()