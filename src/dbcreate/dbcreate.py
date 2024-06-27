# -*-coding: utf-8 -*-

""" This module does the creation of sqlite database
from data tables dataframes and Keys description.
"""

import sys
import os
import pkg_resources

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import argparse
import sqlite3
import pandas as pd
from src.extraction.retrieve_data import GetSpreadsheetData
from dbcreate.erd_create import ERD_maker
from src.extraction.utils import checks_pipeline

class sqliteCreate():
    """
    Class that create a sqlite file based on data from extraction module
    """

    def __init__(self, getData: object, output_dir) -> None:
        assert isinstance(getData, GetSpreadsheetData)
        self.data = getData
        self.output_path = f"{os.path.join(output_dir, self.data.db_name)}.sqlite"
    
    #! check output dir exist or create it
    def create_db(self) -> None:
        """
        Iterate through tables_structure dataframe to create table
        with both PK and FK constraints

        This function create a sqlite file
        """

        db_file = self.output_path
        conn = sqlite3.connect(database=db_file)
        
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

        db_file = self.output_path
        conn = sqlite3.connect(db_file)
        for table in self.data.datatables_list:
            self.data.sheets_dict[table].to_sql(name=table,
                                           con=conn,
                                           if_exists='append',
                                           index=False
                                           )
        return

    def ddict_schema_create(self):
        
        blob_image = self._create_ERD()
        
        sql_statement = self._get_sql()

        conn = sqlite3.connect(database=self.output_path)

        cursor = conn.cursor()

        create_query = (
            "CREATE TABLE IF NOT EXISTS DDict_schema"
            "(ERD, sql_statement)"
        )

        cursor.execute(create_query)

        insert_query = (
            f"INSERT INTO DDict_schema (ERD, sql_statement) VALUES(?,?)"
        )
        cursor.execute(insert_query, (blob_image, sql_statement))

        conn.commit()

        conn.close()

        return None

    def _create_ERD(self):

        try:
            pkg_resources.get_distribution('eralchemy2')
            print("eralchemy")
            draw = ERD_maker(db_path=self.output_path)
            blob_image = draw.eralchemy_draw_ERD()

        except pkg_resources.DistributionNotFound:
            print('networkx')
            draw = ERD_maker(db_path=self.output_path, tables_structure=getData.tables_structure)
            blob_image = draw.networkx_draw_ERD()
        
        return blob_image

    def _get_sql(self):

        conn = sqlite3.connect(database=self.output_path)
        cursor = conn.cursor()
        cursor.execute('SELECT sql from sqlite_master')

        raw_sql = cursor.fetchall()

        sql_statement = str()
        for row in raw_sql:
            if row[0] is not None:
                sql_statement+= row[0] + "\n"
        
        conn.close()

        return sql_statement



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
    parser.add_argument("output_dir", help="absolute path to the output directory")
    args = parser.parse_args()
    
    getData = GetSpreadsheetData(filepath=args.filepath)

    check_funcs_list = [
        getData.check_pk_defined,
        getData.check_pk_uniqueness,
        getData.check_fk_get_ref,
        getData.check_FK_existence_and_uniqueness
    ]
    checks_pipeline(check_funcs_list)

    dbCreate = sqliteCreate(getData, output_dir= args.output_dir)
    dbCreate.create_db()
    dbCreate.insert_data()
    dbCreate.ddict_schema_create()