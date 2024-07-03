"""
    This is not a module and it should not be imported
    Use it only for testing purpose
"""

import sys
import os
import argparse

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from src.utils import checks_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to the spreadsheet you want to convert")
    parser.add_argument("output_dir", help="absolute path to the output directory")
    args = parser.parse_args()
    
    getData = GetSpreadsheetData(filepath=args.filepath)

    #? conf file to store check list
    check_funcs_list = [
        getData.check_no_shared_name,
        getData.check_pk_defined,
        getData.check_pk_uniqueness,
        getData.check_fk_get_ref,
        getData.check_FK_existence_and_uniqueness
    ]
    checks_pipeline(check_funcs_list)

    sqlite_db = sqliteCreate(getData, output_dir= args.output_dir)
    sqlite_db.create_db()
    sqlite_db.insert_data()
    sqlite_db.ddict_schema_create()
    sqlite_db.meta_tables_create()