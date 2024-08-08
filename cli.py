import logging
import argparse
import os

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.check import CheckSpreadsheet,
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate, sqlite2pdf


def main_cli():

    parser = argparse.ArgumentParser(description="Welcome into Ss2db. Let's convert spreadsheets into sqlite databases")

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

    parser.add_argument(
        "-ow",
        "--overwrite",
        nargs="?",
        const=False,
        type=bool,
        help="default False, set on True to overwritte previously generated output"
    )

    parser.add_argument(
        "--filename",
        nargs="?",
        const=str,
        help="basename of output, default behavior will be using spreadsheet name"
    )

    parser.add_argument(
        "--from-sqlite",
        nargs="?",
        const=False,
        type=bool,
        help="default False, set on True if you provide path to sqlite file and want a PDF creation from it only"
    )

    args = parser.parse_args()

    input_path = os.path.normpath(args.input)
    output_path = os.path.normpath(args.output)
    
    if args.from_sqlite == True:
        doc = sqlite2pdf(input_path, output_path)
        doc.createPDF()
    else:
        # check data in spreadsheet is valid
        checker = CheckSpreadsheet(input_path)
        checker.validate_spreadsheet()


        data = GetSpreadsheetData(
                    filepath=input_path,
                    checked_data=checker.sheets_dict
                )
        
        spreadsheet_name = os.path.splitext(os.path.basename(input_path))[0]
    
        if args.overwrite != None and args.filename:
            # overwrite the specified filename if exists
            rm_if_exists(os.path.join(output_path, args.filename + ".sqlite"))
            data.db_name = args.filename
        elif args.overwrite != None and args.filename is None:
            # user overwrite file with default filename if exits
            rm_if_exists(os.path.join(output_path, spreadsheet_name + ".sqlite"))
        elif args.overwrite is None and args.filename:
            # user specified filename but donesn't want to overwrite
            fileExistsHandler(os.path.join(output_path, args.filename + ".sqlite"))
            data.db_name = args.filename
        if args.overwrite is None and args.filename is None:
            # user haven't specified 
            fileExistsHandler(os.path.join(output_path, spreadsheet_name + ".sqlite"))
                
        # create sqlite and erd_schema
        sqlite_db = sqliteCreate(data, output_dir=output_path)
        sqlite_db.create_db()
        sqlite_db.insert_data()
        sqlite_db.ddict_schema_create()
        sqlite_db.meta_tables_create()

        # create pdf
        doc = docCreate(sqlite_db)

        doc.createPDF()

    
def rm_if_exists(filepath):
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass

def fileExistsHandler(filepath):
    """Raise error and log error if file exist"""

    filename = os.path.splitext(os.path.basename(filepath))[0]
    if os.path.isfile(filepath):
    # file already exists and user doesn't specify how to handle it
        logging.error(
            f"{FileExistsError}: {filename} already exists in output directory\n"
            "Overwrite it with -ow --overwritte flag OR specify anothe name using --filename"
        )
        raise FileExistsError(
            f"{filename} already exists in output directory"
            "Overwrite it with -ow --overwritte flag OR specify another filename using --filename"
        )