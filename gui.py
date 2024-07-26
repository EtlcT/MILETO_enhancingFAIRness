import logging
import traceback

import os
import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.extraction.retrieve_data import GetSpreadsheetData
from src.extraction.check import CheckDataError
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate
from src.utils import checks_pipeline

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    encoding="utf-8",
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

# set mode on user system value
ctk.set_appearance_mode("System")

ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ss2db-alpha")
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsw"
        )

        # display instruction to user: chose spreadsheet
        self.browse_file_label = ctk.CTkLabel(
            master=self.input_frame,
            text="Select a spreadsheet to convert into sqlite database"
        )
        self.browse_file_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="w"
        )
        
        # browse button open file dialog
        self.browse_file_btn = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            command=self.browse_file
            )
        self.browse_file_btn.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # display selected file
        self.selected_file = ctk.CTkLabel(master=self.input_frame, text="")
        self.selected_file_grid_options = {
            "row":1,
            "column":0,
            "columnspan":3,
            "padx":10,
            "pady":(10, 0),
            "sticky": "w"
        }
        # hide label while empty
        self.selected_file.grid_forget()

        # display instruction to user: chose output dir
        self.browse_folder_label = ctk.CTkLabel(
            master=self.input_frame,
            text="Select a folder to output sqlite database, ERD schema and PDF documentation"
        )
        self.browse_folder_label.grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="w"
        )

        # Browse button for output folder selection
        self.browse_folder_btn = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            command=self.browse_folder
            )
        self.browse_folder_btn.grid(
            row=2,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )
        
        # display selected folder for output
        self.selected_folder = ctk.CTkLabel(master=self.input_frame, text="")
        self.selected_folder_grid_options = {
            "row":3,
            "column":0,
            "columnspan":3,
            "padx":10,
            "pady":(10, 0),
            "sticky":"w"
        }
        # hide label while empty
        self.selected_folder.grid_forget()

        self.create_sqlite_btn = ctk.CTkButton(master=self)
            
        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=1)

    # open file dialog for spreadsheet selection
    def browse_file(self):
        """Open a file dialog window for spreadsheets files
        then display selected file
        """
        self.filepath = ctk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All Excel files", "*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt")]
        )
        if self.filepath:
            self.update_labels(
                self.selected_file,
                f"Selected file: {self.filepath}",
                grid_option=self.selected_file_grid_options
            )
        
        self.display_proccess_btn()

    # open file dialog for output directory selection
    def browse_folder(self):
        """Open a file dialog window for output directory selection"""
        self.folder_path = ctk.filedialog.askdirectory(
            title="Select a directory for output (sqlite database, ERD schema and PDF documentation)"
            )
        if self.folder_path:
            self.update_labels(
                self.selected_folder,
                f"Selected folder: {self.folder_path}",
                grid_option=self.selected_folder_grid_options
                )
        
        self.display_proccess_btn()

    # display sqlite btn
    def display_proccess_btn(self):
        """Display create sqlite btn if user selected both spreadsheet
        and output directory
        """
        if (self.selected_file.cget("text") != "" and
            self.selected_folder.cget("text") != ""):
                self.create_sqlite_btn = ctk.CTkButton(
                master=self,
                text="Create sqlite",
                command=lambda: self.ask_confirm(
                    question=(
                        'Do you want to create sqlite database for the following spreadsheet ?\n'
                        f'{self.filepath}\n'
                        f'Results will be saved into: {self.folder_path}'
                        )
                    )
                )
                self.create_sqlite_btn.grid(
                    row=1,
                    column=0,
                    padx=10,
                    pady=10
                )
        else:
            self.create_sqlite_btn.grid_forget()

    def update_labels(self, label, value, grid_option=None):
        """Update the selected label text attribute with value"""
        label.configure(text=value)
        if grid_option is not None:
            label.grid(**grid_option)

    def sqlite_create(self):
        """Display progress bar and labels relative to the process
        Run function from extraction and db_create module to generate
        sqlite file and ERD schema
        """

        # Create frame for processing info
        self.running_process_frame = ctk.CTkFrame(self)
        self.running_process_frame.grid(
            row=1,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew"
        )
        self.running_process_frame.grid_columnconfigure(0, weight=0)
        self.running_process_frame.grid_columnconfigure(1, weight=0)
        self.running_process_frame.grid_columnconfigure(2, weight=1)

        # Label for progress bar
        self.progress_bar_label = ctk.CTkLabel(
            master=self.running_process_frame,
            text="Creating sqlite and ERD"
        )
        self.progress_bar_label.grid(
            row=1,
            column=0,
            padx = 20,
            pady=10
        )

        # label for task running
        self.task_label = ctk.CTkLabel(
            master=self.running_process_frame,
            text=""
        )
        self.task_label.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

        # Progress bar
        self.sqlite_create_progress = ctk.CTkProgressBar(
            master=self.running_process_frame,
            determinate_speed=4.5,
            width=100,
            height=25
        )
        self.sqlite_create_progress.grid(
            row=1,
            column=1,
        )

        # instantiate progress bar at 0
        self.sqlite_create_progress.set(0)
        self.sqlite_create_progress.start()

        spreadsheet_path = os.path.normpath(self.filepath)
        output_directory = os.path.normpath(self.folder_path)
        try:
            self.data = GetSpreadsheetData(filepath=spreadsheet_path)
        except RuntimeError as e:
            self.show_error(msg=f"Spreadsheet validation failed because of the following error(s):\n {e}")
            self.sqlite_create_progress.destroy()

        
        sqlite_db = sqliteCreate(getData=self.data, output_dir=output_directory)

        sqlite_db.create_db()
        sqlite_db.insert_data()
        sqlite_db.ddict_schema_create()
        sqlite_db.meta_tables_create()

        self.sqlite_create_progress.stop()
        self.sqlite_create_progress.destroy()

        # try:
        #     self.task_label.configure(text="Retrieving data from spreadsheet")
        #     self.data = GetSpreadsheetData(filepath=spreadsheet_path)
        #     self.sqlite_create_progress.step()
        #     self.sqlite_create_progress.update()

        #     # test from extraction module to run before db creation
        #     tests_steps = [
        #         {"function": self.data.check_no_shared_name, "label": "Checking different fields have different names"},
        #         {"function": self.data.check_pk_defined, "label": "Checking each table have a PK defined"},
        #         {"function": self.data.check_pk_uniqueness, "label": "Checking PK fields have no duplicate"},
        #         {"function": self.data.check_fk_get_ref, "label": "Checking FK fields have a reference table defined"},
        #         {"function": self.data.check_FK_existence_and_uniqueness, "label": "Checking FK fields exist in reference table and have no duplicate"}
        #     ]
            
        #     errors = []
        #     for task in tests_steps:
        #         self.task_label.configure(text=task["label"])
        #         try:
        #             task["function"]()
        #         except:
        #             logging.error(f"Exception occurred in {task["function"]().__name__}: {str(e)}", exc_info=True)
        #             logging.error(traceback.format_exc(), exc_info=True)
        #             errors.append(f"Exception in {task["function"]().__name__}: {str(e)}")
        #         self.sqlite_create_progress.step()
        #         self.sqlite_create_progress.update()

        #     sqlite_db = sqliteCreate(getData=self.data, output_dir=output_directory)
        #     self.sqlite_create_progress.step()

        #     db_create_steps = [
        #         {"function": sqlite_db.create_db, "label": "Creating sqlite"},
        #         {"function": sqlite_db.insert_data, "label": "Inserting data in database"},
        #         {"function": sqlite_db.ddict_schema_create, "label": "Creating and inserting ERD"},
        #         {"function": sqlite_db.meta_tables_create, "label": "Inserting metadata tables"}
        #     ]

        #     for task in db_create_steps:
        #         self.task_label.configure(text=task["label"])
        #         task["function"]()
        #         self.sqlite_create_progress.step()
        #         self.sqlite_create_progress.update()

        #     self.sqlite_create_progress.set(1)
        #     self.sqlite_create_progress.update()
        #     self.show_success(
        #         msg=f"sqlite database of {self.data.db_name} successfully created !"
        #     )

        #     self.running_process_frame.grid_forget()
        
        # except Exception as e:
        #     logging.error("An error occurred", exc_info=True)
        #     traceback.print_exc()
        #     self.show_error(msg=f"An error occured: {e}")

        # pdf_doc = docCreate(getData=self.data, output_dir=output_directory)
        # pdf_doc.sql_dump = sqlite_db.sql_dump
        # pdf_doc.createPDF()

    def show_success(self, msg):
        """ Open Window with success message"""
        CTkMessagebox(
            master=self,
            title="Success",
            message=msg,
            icon="check",
            option_1="OK"
        )
    
    def show_error(self, msg):
        """Open window with error message"""
        CTkMessagebox(
            master=self,
            title="ERROR",
            message=msg,
            icon="cancel",
            option_1="OK"
        )
    
    def ask_confirm(self, question):
        msg = CTkMessagebox(
            title="Confirm ?",
            message=question,
            icon="question",
            option_1="Cancel",
            option_2="Yes",
        )
        
        response = msg.get()

        if response == "Yes":
            self.sqlite_create()
        else:
            msg.destroy()


def main_gui():
    app = App()
    app._state_before_windows_set_titlebar_color = 'zoomed'
    app.mainloop()