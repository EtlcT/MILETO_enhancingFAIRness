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
    from src.extraction.check import CheckSpreadsheet, InvalidData
    from src.dbcreate.dbcreate import sqliteCreate
    from src.doccreate.pdf_create import docCreate

except Exception as e:
    logging.error("An error occurred", exc_info=True)

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

    args = parser.parse_args()

    input_path = os.path.normpath(args.input)
    output_path = os.path.normpath(args.output)
    
    # check data in spreadsheet is valid
    checker = CheckSpreadsheet(input_path)
    checker.validate_spreadsheet()


    data = GetSpreadsheetData(
                filepath=input_path,
                checked_data=checker.sheets_dict
            )
 
    if os.path.isfile(os.path.join(output_path, os.path.splitext(os.path.basename(input_path))[0] + ".sqlite")):
        # if sqlite file for this spreadsheet already exists in output directory
        if args.overwrite != None:
            # if user specifies he want the file to be overwritten, delete sqlite
            os.remove(os.path.join(output_path, os.path.splitext(os.path.basename(input_path))[0] + ".sqlite"))
        elif args.filename:
            # if user specifies another filename as output instead of spreadsheet name
            data.db_name =args.filename
        else:
            # file already exists and user doesn't specify how to handle it
            logging.error(
                f"{FileExistsError}: {os.path.splitext(os.path.basename(input_path))[0]} already exists"
                "Overwrite it with -ow --overwritte flag OR specify anothe name using --filename"
                )
            
    # create sqlite and erd_schema
    sqlite_db = sqliteCreate(data, output_dir=output_path)
    sqlite_db.create_db()
    sqlite_db.insert_data()
    sqlite_db.ddict_schema_create()
    sqlite_db.meta_tables_create()

    # create pdf
    doc = docCreate(sqlite_db)

    doc.createPDF()