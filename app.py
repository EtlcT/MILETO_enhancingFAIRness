import sys
import os

from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from src.utils import checks_pipeline

def main():
    print('Welcome into Spreadsheet2sqlite\nEnter exit or Ctrl+C to quit.\n')

    while True:
        try:
            user_input = input("Please provide the absolute pathfile to your spreadsheet\n")

            if user_input=='exit':
                print('Thank your for using Spreadsheet2Sqlite')
                break

            else:
                
                output_dir = input("Please provide the output directory to save .sqlite .png and .pdf files\n")

                file_path = os.path.normpath(user_input)
                
                data = GetSpreadsheetData(filepath=file_path)

                check_funcs_list = [
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
            with open('logs.txt','a+') as logfile:
                logfile.write(f"{e}\n")


if __name__=='__main__':
    
    main()