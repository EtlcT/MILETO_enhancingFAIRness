import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

class View(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ss2db")
        self.controller = None
        self.createWidgets()
        self.sheets_dict = None

    def createWidgets(self):

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew"
        )

        self.input_frame.grid_columnconfigure(0, weight=1)

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

    def set_controller(self, controller):
        self.controller = controller

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

            self.checkSpreadsheet = ctk.CTkButton(
                master=self.input_frame,
                text="Verify spreadsheet",
                command=self.verify_spreadsheet
            )
            self.checkSpreadsheet.grid(
                    row=2,
                    column=0,
                    padx=10,
                    pady=10
                )
    
    def update_labels(self, label, value, grid_option=None):
        """Update the selected label text attribute with value"""
        label.configure(text=value)
        if grid_option is not None:
            label.grid(**grid_option)
    
    def verify_spreadsheet(self):

        # remove previous errors from view
        if hasattr(self, "error_frame"):
            self.error_frame.destroy()

        if self.controller:
            self.controller.verify_spreadsheet(self.filepath)
    
    def display_errors(self, error_msg):
        """Add frame in input frame to show errors to user"""

        self.error_frame = ctk.CTkFrame(master=self.input_frame)
        self.error_frame.grid(
            row=3
        )
        self.error_icon = ctk.CTkImage(
            light_image=Image.open(os.path.join("src/gui/assets/error.png")),
            size=(40,40)
            )
        self.error_icon_label = ctk.CTkLabel(master=self.error_frame, image=self.error_icon, text="")
        self.error_icon_label.grid(
            row=0,
            column=0,
        )
        
        self.errors = ctk.CTkLabel(master=self.error_frame, text=error_msg, justify="left")
        self.errors.grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

    def display_sheet(self, sheet_name):
        """Update the frame that contain spreadsheet"""

        self.sheet["column"] = list(self.sheets_dict[sheet_name].columns)
        self.sheet["show"] = "headings"
        for column in self.sheet["columns"]:
            self.sheet.heading(column, text=column)
        
        df_rows = self.sheets_dict[sheet_name].head(10).to_numpy().tolist()
        for row in df_rows:
            self.sheet.insert("", "end", values=row)     

    def sheet_selection_callback(self, choice):
        """Update frame base on sheet selection"""

        self.sheet.delete(*self.sheet.get_children())
        self.display_sheet(sheet_name=choice)


    def display_data(self):
        """Add frame that that shows sheet and 
        menu to switch from one sheet to another
        """

        self.spreadsheet_frame = ctk.CTkFrame(
            master=self
        )
        self.spreadsheet_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.spreadsheet_frame.grid_columnconfigure(0, weight=1)

        self.sheet_selection = ctk.CTkComboBox(
            master=self.spreadsheet_frame,
            values=list(self.sheets_dict.keys()),
            command=self.sheet_selection_callback
        )
        self.sheet_selection.grid(
            row=0,
            column=0,
            sticky="w"
            )
        
        self.sheet = ttk.Treeview(
            master=self.spreadsheet_frame
        )
        self.sheet.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

