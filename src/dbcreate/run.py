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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input", 
        help="Absolute path to the spreadsheet to convert",
        required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Absolute path to the output directory of your choice",
        required=True
    )
    args = parser.parse_args()
    
    getData = GetSpreadsheetData(filepath=args.input)

    sqlite_db = sqliteCreate(getData, output_dir= args.output)
    sqlite_db.create_db()
    sqlite_db.insert_data()
    sqlite_db.ddict_schema_create()
    sqlite_db.meta_tables_create()