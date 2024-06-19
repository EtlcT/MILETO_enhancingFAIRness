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

class sqliteCreate():
    """
    Class that create a sqlite file based on data from extraction module
    """

    def __init__(self, getData: object) -> None:
        assert isinstance(getData, GetSpreadsheetData)
        self.data = getData

    def create_db(self) -> None:
        """
        Iterate through table_structure dataframe to create table
        with both PK and FK constraints

        This function create a sqlite file
        """

        filename = f"{self.data.db_name}.sqlite"
        conn = sqlite3.connect(database=filename)
        
        group_by_table = self.data.table_structure.groupby(by='Table')
        for table_name, table_info in group_by_table:

            column_list = table_info['Attribute'].tolist()
            pk_attr = table_info[table_info['isPK']=='Y']['Attribute']
            fk_info = table_info[table_info['isFK']=='Y'][['Attribute', 'ReferenceTable']]

            query = self._add_PK_constraint(table_name, column_list, pk_attr)

            # if there are some FK constraint            
            if (fk_info.empty != True):
                fk_statement = self._add_FK_constraint(fk_info)
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

    def _add_FK_constraint(self, fk_info: pd.DataFrame) -> str:
        """
        Return a part of sql statement relative to Foreign keys constraint
        FOREIGN KEYS (field_name) REFERENCES ref_table_name(field_name)
        
        fk_info: pandas.Dataframe
            columns:
                Name: Attribute, type: str, detail: FK attribute
                Name: ReferenceTable, type: str, detail: the parent table

        !!WARNING!! field name must be the same in child and parent table
        """

        fk_statement = str()
        for index, row in fk_info.iterrows():
            fk_statement += f", FOREIGN KEY ({row['Attribute']}) REFERENCES {row['ReferenceTable']}"
        return fk_statement
            


    #? function not working for sqlite db
    #? ALTER TABLE not supported
    # def create_db(self) -> None:
    #     """
    #     Iterate through keys in self.dict_tables (ie: table name)
    #     if the table is part of data table, it is created in the database
    #     """
    #     conn = sqlite3.connect(database=self.dbname)

    #     for table in self.dict_tables:
    #         if table in self.datatable_list:
    #             self.dict_tables[table].to_sql(
    #                 name=table,
    #                 con=conn,
    #                 if_exists='replace',
    #                 index=False
    #             )
    #     conn.close()

    # def add_constraint(self) -> None:
    #     """
    #     Add constraints relative to PK, FK and NULLABLE fields based 
    #     on keys table (ie self.keys)
    #     """
    #     conn = sqlite3.connect(database=self.dbname)
    #     for _, row in self.keys.iterrows():
            
    #         table = row['Table']
    #         field = row['Atttribute']
    #         reference = row['References']

    #         if row['isPK']=='Y':
    #             conn.execute(
    #                 f"ALTER TABLE {table} ADD PRIMARY KEY ({field})"
    #             )
    #         elif row['isFK']=='Y':
    #             conn.execute(f'ALTER TABLE {table} ADD FOREIGN KEY ({field}) REFERENCES {reference}({field})')
    #     conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to the spreadsheet you want to convert")
    args = parser.parse_args()
    # if args.filepath is None:
    #     raise TypeError("filepath to your spreadsheet is required")
    getData = GetSpreadsheetData(filepath=args.filepath)
    dbCreate = sqliteCreate(getData)
    dbCreate.create_db()
    dbCreate.insert_data()