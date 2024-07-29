import logging
import argparse
import os

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s', 
                    handlers=[logging.FileHandler("logs"),
                              logging.StreamHandler()])
try:
    from src.extraction.retrieve_data import GetSpreadsheetData
    from src.extraction.check import InvalidData
    from src.dbcreate.dbcreate import sqliteCreate
    from src.doccreate.pdf_create import docCreate

except Exception as e:
    logging.error("An error occurred", exc_info=True)

def main_cli():

    parser = argparse.ArgumentParser(description="Welcome into Ss2db. Let's convert spreadsheets into sqlite databases")

    parser.add_argument(
        '-i',
        '--input', 
        help='Absolute path to the spreadsheet to convert',
        required=True
    )

    parser.add_argument(
        '-o',
        '--output',
        help='Absolute path to the output directory of your choice',
        required=True
    )

    args = parser.parse_args()

    input_path = os.path.normpath(args.input)
    output_path = os.path.normpath(args.output)
    
    data = GetSpreadsheetData(filepath=input_path)

    sqlite_db = sqliteCreate(data, output_dir=output_path)
    sqlite_db.create_db()
    sqlite_db.insert_data()
    sqlite_db.ddict_schema_create()
    sqlite_db.meta_tables_create()

    doc = docCreate(sqlite_db)

    doc.createPDF()