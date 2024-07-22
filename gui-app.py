import logging
import traceback
import sys
import os
import customtkinter as ctk
import tkinter as tk
from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from src.doccreate.pdf_create import docCreate

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

        self.process_btn = ctk.CTkButton(
            master=self,
            command=self.run_code
        )
        self.process_btn.grid(
            row=1,
            column=0,
            padx=10,
            pady=10
        )


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
        
     
    def update_labels(self, label, value, grid_option=None):
        """Update the selected label text attribute with value"""
        label.configure(text=value)
        if grid_option is not None:
            label.grid(**grid_option)

    def run_code(self):
        
        spreadsheet_path = os.path.normpath(self.filepath)
        output_directory = os.path.normpath(self.folder_path)

        data = GetSpreadsheetData(filepath=spreadsheet_path)
        data.check_no_shared_name()
        data.check_pk_defined()
        data.check_pk_uniqueness()
        data.check_fk_get_ref()
        data.check_FK_existence_and_uniqueness()

        sqlite_db = sqliteCreate(getData=data, output_dir=output_directory)
        sqlite_db.create_db()
        sqlite_db.insert_data()
        sqlite_db.ddict_schema_create()
        sqlite_db.meta_tables_create()

        pdf_doc = docCreate(getData=data, output_dir=output_directory)
        pdf_doc.sql_dump = sqlite_db.sql_dump
        pdf_doc.createPDF()

        print("\nYour spreadsheet has been converted successfully !")


if __name__ == "__main__":
    app = App()
    # app.attributes("-fullscreen", "True")
    app.mainloop()