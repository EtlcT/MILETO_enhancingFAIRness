import logging
import traceback
import sys
import os

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s', 
                    handlers=[logging.FileHandler("error.log"),
                              logging.StreamHandler()])

try:
    from src.extraction.retrieve_data import GetSpreadsheetData
    from src.dbcreate.dbcreate import sqliteCreate
    from src.doccreate.pdf_create import docCreate
    from src.utils import checks_pipeline
except Exception as e:
    logging.error("An error occurred", exc_info=True)
    traceback.print_exc()

def main():
    print('Welcome into Ss2db\nEnter exit or Ctrl+C to quit.\n')

    while True:
        try:
            user_input = input("Please provide the absolute pathfile to your spreadsheet\n")

            if user_input=='exit':
                print('Thank your for using Ss2db')
                break

            else:
                
                file_path = os.path.normpath(user_input)

                output_dir = input("Please provide the output directory to save .sqlite .png and .pdf files\n")

                output_path = os.path.normpath(output_dir)

                user_confirm = input(f"Do you confirm that you want to output file into {output_path} ? Enter 'y' to confirm\n")

                if user_confirm.lower() == 'y':

                    data = GetSpreadsheetData(filepath=file_path)

                    check_funcs_list = [
                        data.check_no_shared_name,
                        data.check_pk_defined,
                        data.check_pk_uniqueness,
                        data.check_fk_get_ref,
                        data.check_FK_existence_and_uniqueness
                    ]
                    checks_pipeline(check_funcs_list)

                    # create sqlite and erd.png
                    sqlite_db = sqliteCreate(getData=data, output_dir=output_path)
                    sqlite_db.create_db()
                    sqlite_db.insert_data()
                    sqlite_db.ddict_schema_create()
                    sqlite_db.meta_tables_create()

                    # create documentation
                    pdf_doc = docCreate(getData=data, output_dir=output_path)
                    pdf_doc.sql_dump = sqlite_db.sql_dump
                    pdf_doc.createPDF()

                    print("\nYour spreadsheet has been converted successfully !")
                
        except Exception as e:
            logging.error("An error occurred", exc_info=True)
            traceback.print_exc()


if __name__=='__main__':
    
    main()