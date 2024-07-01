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
    from src.utils import checks_pipeline, resource_path
except Exception as e:
    logging.error("An error occurred", exc_info=True)
    traceback.print_exc()

def main():
    print('Welcome into Spreadsheet2sqlite\nEnter exit or Ctrl+C to quit.\n')

    while True:
        try:
            user_input = input("Please provide the absolute pathfile to your spreadsheet\n")

            if user_input=='exit':
                print('Thank your for using Spreadsheet2Sqlite')
                break

            else:
                
                file_path = os.path.normpath(user_input)

                output_dir = input("Please provide the output directory to save .sqlite .png and .pdf files\n")

                data = GetSpreadsheetData(filepath=file_path)

                check_funcs_list = [
                    data.check_no_shared_name,
                    data.check_pk_defined,
                    data.check_pk_uniqueness,
                    data.check_fk_get_ref,
                    data.check_FK_existence_and_uniqueness
                ]
                checks_pipeline(check_funcs_list)

                dbCreate = sqliteCreate(data, output_dir=output_dir)
                dbCreate.create_db()
                dbCreate.insert_data()
                dbCreate.ddict_schema_create()
                
        except Exception as e:
            logging.error("An error occurred", exc_info=True)
            traceback.print_exc()


if __name__=='__main__':
    
    main()