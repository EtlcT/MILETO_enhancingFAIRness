# -*-coding: utf-8 -*-

""" This module creates sqlite database
from data tables dataframes and tables_info description.
"""

import sys
import os
import pkg_resources
import sqlite3
import pandas as pd

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from conf.config import *
from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.erd_create import ERD_maker



class sqliteCreate():
    """
    Class that create a sqlite file based on data from extraction module
    """

    def __init__(self, getData: object, output_dir: str) -> None:
        assert isinstance(getData, GetSpreadsheetData), (
            "Error getData should be an instance of sqliteCreate class"
            )
        self.data = getData
        self.output_dir = output_dir
        self.output_sqlite = os.path.normpath((output_dir + '/' + self.data.db_name + '.sqlite'))
        self.sql_dump = str()
    
    #! check output dir exist or create it
    def create_db(self) -> None:
        """
        Iterate through tables_info dataframe to create table
        with both PK and FK constraints
        CHANGES:  also specify data types

        This function create a sqlite file
        """

        db_file = self.output_sqlite
        conn = sqlite3.connect(database=db_file)
        
        group_by_table = self.data.tables_info.groupby(by=INFO_ATT['table'])
        for table_name, table_info in group_by_table:

            # looks for composite pk
            pk_attr = table_info[table_info[INFO_ATT['isPK']]=='Y'][INFO_ATT['attribute']].tolist()
            attr_list = table_info[INFO_ATT['attribute']].tolist()
            attr_type = table_info['type'].tolist()

            if len(pk_attr) > 1:
                # if PK is composite
                attr_statement = ",\n    ".join(
                    [f"{item1} {item2}" for item1, item2 in zip(attr_list, attr_type)]
                )

                query = (
                    f"CREATE TABLE {table_name}(\n"
                    f"    {attr_statement},\n"
                    f"    PRIMARY KEY ({', '.join([pk_field_name for pk_field_name in pk_attr])})"
                )

            else:
                # if PK not composite
                # find index in attr_list to access its type
                index = attr_list.index(f'{pk_attr[0]}')
                
                attr_statement = ",\n    ".join(
                    [f"{item1} {item2}" for item1, item2 in zip(attr_list, attr_type)]
                )
                
                attr_statement = attr_statement.replace(
                    f"{pk_attr[0]} {attr_type[index]}",
                    f"{pk_attr[0]} {attr_type[index]} PRIMARY KEY"
                )
                
                query = (
                    f"CREATE TABLE {table_name}(\n"
                    f"    {attr_statement}"
                )

            isFK_condition = ~table_info[INFO_ATT['isFK']].isna()
            group_by_table_ref = (
                table_info[isFK_condition]
                .groupby(INFO_ATT['refTable'])
            )

            for ref_table_name, ref_info in group_by_table_ref[[INFO_ATT['attribute'],INFO_ATT['refTable']]]:

                fk_statement = self._add_FK_constraint(
                    ref_table_name=ref_table_name,
                    fk_attribute=ref_info[INFO_ATT['attribute']].tolist()
                )
                query += f"{fk_statement}"
            
            query += "\n)\n"
            self.sql_dump+=query
            conn.execute(query)

        conn.close()

        return 

    def insert_data(self) -> None:
        """
        Process data and insert it into database
        """

        db_file = self.output_sqlite
        conn = sqlite3.connect(db_file)

        for table in self.data.datatables_list:

            self.data.sheets_dict[table].to_sql(
                name=table,
                con=conn,
                if_exists='append',
                index=False             
            )

        conn.close()

        return

    def meta_tables_create(self) -> None:
        """ Create non data table
        """
        db_file = self.output_sqlite
        conn = sqlite3.connect(db_file)

        for table in TEMP_CONF.keys():
            if table != "DDict_schema":
                tab_name = TEMP_CONF[table]["tab_name"]
                self.data.sheets_dict[tab_name].to_sql(
                    name=tab_name,
                    con=conn,
                    if_exists='replace',
                    index=False
                )

        conn.close()

        return None

    def ddict_schema_create(self) -> None:
        """
        Create DDict_schema table and 
        insert the Entity-Relationship Diagram and sql statement
        """

        blob_image = self.create_ERD()
        
        sql_statement = self.sql_dump

        conn = sqlite3.connect(database=self.output_sqlite)

        create_query = (
            "CREATE TABLE IF NOT EXISTS DDict_schema"
            "(ERD BLOB, sql_statement TEXT)"
        )

        conn.execute(create_query)

        insert_query = (
            f"INSERT INTO DDict_schema (ERD, sql_statement) VALUES(?,?)"
        )

        conn.execute(insert_query, (blob_image, sql_statement))
        
        conn.commit()

        conn.close()

        return

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
            f",\n    FOREIGN KEY ({(', ').join(fk_attribute)}) "
            f"REFERENCES {ref_table_name}({(', ').join(fk_attribute)})"
        )
        
        return fk_statement

    def create_ERD(self) -> bytes:
        """Create ERD schema, save it as svg
        and return it as a Blob
        """

        draw = ERD_maker(
            db_name= self.data.db_name,
            output_dir= self.output_dir,
            tables_infos= self.data.tables_info
        )

        blob_image = draw.create_erd()
        
        return blob_image

    # def get_sql(self) -> str:
    #     """ Return sql statement that lead to this database creation
    #     """

    #     conn = sqlite3.connect(database=self.output_sqlite)
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT sql from sqlite_master WHERE sql IS NOT NULL')

    #     raw_sql = cursor.fetchall()

    #     cursor.close()
    #     conn.close()

    #     formatted_sql = prettier_sql(raw_sql)

    #     self.sql_dump = formatted_sql

    #     return formatted_sql
    
    