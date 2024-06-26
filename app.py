import sys
import os

from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from src.extraction.utils import checks_pipeline

# def get_application_path():
#     """
#     Get the path where the application is running.
#     """
#     if getattr(sys, 'frozen', False):
#         # Running in a bundle
#         print('bundle')
#         return os.path.dirname(sys.executable)
#     else:
#         # Running in a normal Python environment
#         print('frozen')
#         return os.path.dirname(os.path.abspath(__file__))

def main():
    print(os.getcwd())
    print('Welcome into Spreadsheet2sqlite\nEnter exit or Ctrl+C to quit.\n')

    while True:
        try:
            print("Please provide the absolute pathfile to your spreadsheet\n")
            user_input = input()

            if user_input=='exit':
                print('Thank your for using Spreadsheet2Sqlite')
                break

            else:
                file_path = os.path.normpath(user_input)
                
                data = GetSpreadsheetData(filepath=file_path)

                check_funcs_list = [
                    data.check_pk_defined,
                    data.check_pk_uniqueness,
                    data.check_fk_get_ref,
                    data.check_FK_existence_and_uniqueness
                ]
                checks_pipeline(check_funcs_list)

                dbCreate = sqliteCreate(data)
                dbCreate.create_db()
                dbCreate.insert_data()
                
        except Exception as e:
            print("An error occured: ", e)


if __name__=='__main__':
    
    main()