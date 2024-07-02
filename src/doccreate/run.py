import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to the spreadsheet you want to convert")
    parser.add_argument("output_dir", help="absolute path to the output directory")
    args = parser.parse_args()
    
    data = GetSpreadsheetData(filepath=args.filepath)

    sqlite_db = sqliteCreate(getData=data, output_dir=args.output_dir)

    doc = docCreate(getData=data, output_dir=args.output_dir)

    doc.createPDF()