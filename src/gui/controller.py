import os
import logging
from tkinter import ttk
import customtkinter as ctk
from PIL import Image

from src.gui.view import View
from src.gui.model import Model
from src.extraction.check import InvalidData
from src.utils.utils import resource_path

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view


    def spreadsheet_loader(self, spreadsheet_path):
        """Display path to selected spreadsheet and load it
        Display button to check data validity
        """
        
        #delete previous content if exist
        self.view.rm_widget("selected_file")

        # display selected file in view input_frame
        selected_file = ctk.CTkLabel(
            master=self.view.input_frame,
            text=spreadsheet_path
        )
        selected_file_gridoptions = {
            "row":1,
            "column":0,
            "columnspan":3,
            "padx":10,
            "pady":(10, 0),
            "sticky": "w"
        }
        self.add_widget(
            widget=selected_file,
            widget_name="selected_file",
            widget_grid=selected_file_gridoptions
        )

        # load excel
        tmp_data = self.load_spreadsheet(spreadsheet_path)

        # display spreadsheet and dropmenu for sheet selection
        self.display_spreadsheet()
        self.display_sheet_selector(tmp_data)

        # Add check button to check data consistency 
        check_btn = ctk.CTkButton(
            master=self.view.input_frame,
            text="Check Spreadsheet data",
            command=self.verify_spreadsheet
        )
        check_btn_gridoptions = {
            "row":3,
            "column":0,
            "padx":10,
            "pady":10
        }
        self.add_widget(
            widget=check_btn,
            widget_name="check_btn",
            widget_grid=check_btn_gridoptions
        )

    def load_spreadsheet(self, spreadsheet_path):
        """Load spreadsheet data"""
        self.model.input_path = spreadsheet_path
        tmp_data = self.model.load_spreadsheet(spreadsheet_path)
        return tmp_data
    
    def display_spreadsheet(self):
        """Add frame with treeview widget to display spreadsheet"""

        # create new frame in view to contain spreadsheet
        spreadsheet_frame = ctk.CTkFrame(
            master=self.view.input_frame
        )
        spreadsheet_frame.grid_columnconfigure(0, weight=1)
        spreadsheet_frame_gridoptions= {
            "row":2,
            "column":0,
            "sticky":"nsew"
        }
        self.add_widget(
            widget=spreadsheet_frame,
            widget_name="spreadsheet_frame",
            widget_grid=spreadsheet_frame_gridoptions
        )

        # create treeview widget in spreadsheet_frame to display sheet
        sheet = ttk.Treeview(
            master=self.view.additional_widgets.get("spreadsheet_frame")
        )
        sheet_gridoptions = {
            "row": 1,
            "column":0,
            "sticky":"nsew"
        }
        self.add_widget(
            widget=sheet,
            widget_name="sheet",
            widget_grid=sheet_gridoptions
        )
    
    def display_sheet(self, tmp_data, selected_sheet):
        """Called on sheet_selector's changes
        Update treeview widget to display selected sheet
        """

        sheet = self.view.additional_widgets.get("sheet")
        sheet["column"] = list(tmp_data[selected_sheet].columns)
        sheet["show"] = "headings"
        for column in sheet["columns"]:
            sheet.heading(column, text=column)
        
        df_rows = tmp_data[selected_sheet].head(20).to_numpy().tolist()
        for row in df_rows:
            sheet.insert("", "end", values=row)

    def display_sheet_selector(self, tmp_data):
        """Add dropmenu for sheet selection to view"""

        # add dropmenu for sheet selection
        def sheet_selection_callback(choice, tmp_data):
            self.view.delete_elmt("sheet")
            self.display_sheet(tmp_data, choice)
            
        sheet_selection = ctk.CTkComboBox(
            master=self.view.get_widget("spreadsheet_frame"),
            values=list(tmp_data.keys()),
            command=lambda choice : sheet_selection_callback(choice, tmp_data)
        )
        sheet_selection_gridoptions = {
            "row":0,
            "column":0,
            "sticky":"w"
        }
        self.add_widget(
            widget=sheet_selection,
            widget_name="sheet_selection",
            widget_grid=sheet_selection_gridoptions
        )

    def verify_spreadsheet(self):
        """Control spreadsheet is conform
        if not display errors
        else display browse directory for output and convert button
        """

        # remove previous errors
        self.view.rm_widget("error_frame")

        try:
            self.model.verify_spreadsheet()
        except InvalidData as e:
            self.display_errors(str(e).replace("str: ", ""))
        # TODO catch other type of exception
        else:
            self.view.show_success("Valid spreadsheet provided")
            self.display_conversion_frame()

    def display_errors(self, error_msg):
        """Add frame in view to show errors in spreadsheet data"""

        # create frame that contains errors
        error_frame = ctk.CTkFrame(master=self.view.input_frame)
        error_frame_gridoptions = {
            "row":4
        }
        self.add_widget(
            widget=error_frame,
            widget_name="error_frame",
            widget_grid=error_frame_gridoptions
        )

        # create error icon
        error_icon_img = ctk.CTkImage(
            light_image=Image.open(os.path.normpath(resource_path("src/gui/assets/error.png"))),
            size=(40,40)
        )
        error_icon = ctk.CTkLabel(master=self.view.get_widget("error_frame"), image=error_icon_img, text="")
        error_icon_gridoptions = {
            "row":0,
            "column":0
        }
        self.add_widget(
            widget=error_icon,
            widget_name="error_icon",
            widget_grid=error_icon_gridoptions
        )
        
        # create label which contains errors
        errors = ctk.CTkLabel(master=self.view.get_widget("error_frame"), text=error_msg, justify="left")
        errors_gridoptions = {
            "row":0,
            "column":1,
            "padx":10,
            "pady":5
        }
        self.add_widget(
            widget=errors,
            widget_name=errors,
            widget_grid=errors_gridoptions
        )
    
    def display_conversion_frame(self):
        """Called once verify_spreadsheet
        Add a conversion frame to view with:
        - browse folder button for output directory selection
        - conversion option radio buttons
        (generate all, only sqlite and erd)
        """

        # TODO : ADD radiobuttons and code action
        # create conversion_frame
        conversion_frame = ctk.CTkFrame(master=self.view)
        conversion_frame.grid_columnconfigure(0, weight=1)
        conversion_frame_gridoptions = {
            "row":2,
            "column":0,
            "sticky":"we"
        }
        self.add_widget(
            widget=conversion_frame,
            widget_name="conversion_frame",
            widget_grid=conversion_frame_gridoptions
        )

        # create label to show selected output directory
        outdir_label = ctk.CTkLabel(
            master=self.view.get_widget("conversion_frame"),
            text="Select a directory to store outputs"
        )
        outdir_label_gridoptions = {
            "row":0,
            "column":0
        }
        self.add_widget(
            widget=outdir_label,
            widget_name="outdir_label",
            widget_grid=outdir_label_gridoptions
        )

        # create button browse folder that open file dialog
        outdir_btn = ctk.CTkButton(
            master=self.view.get_widget("conversion_frame"),
            command=self.view.browse_outdir,
            text="Browse Folder"
        )
        outdir_btn_gridoptions = {
            "row":0,
            "column":1
        }
        self.add_widget(
            widget=outdir_btn,
            widget_name="outdir_btn",
            widget_grid=outdir_btn_gridoptions
        )

    def display_convert_option(self, output_sqlite):
        """Check if file exists in output directory"""

        convert_btn = ctk.CTkButton(
            master=self.view.get_widget("conversion_frame"),
            text="Convert spreadsheet",
            command=self.convert,
            state="disabled"
        )
        convert_btn_gridoptions = {
            "row":2,
            "column":0,
            "sticky": "nsew",
            "columnspan":2
        }
        self.add_widget(
            widget=convert_btn,
            widget_name="convert_btn",
            widget_grid=convert_btn_gridoptions
        )

        if os.path.isfile(output_sqlite):
            # an output already exists for this spreadsheet

            # Add warning message to error_frame ask user how to handle existing files
            file_exists_warning_msg = ( 
                f"WARNING: An sqlite file already exist in output directory for this spreadsheet"
                "\nCheck the overwrite checkbox to delete existing file"
                " or provide another filename: "
            )
            file_exists_warning = ctk.CTkLabel(
                master=self.view.get_widget("conversion_frame"),
                text=file_exists_warning_msg
            )
            file_exists_warning_grid = {
                "row":1,
                "column":0
            }
            self.add_widget(
                widget=file_exists_warning,
                widget_name="file_exists_warning",
                widget_grid=file_exists_warning_grid
            )

            def callback_entry(*args):
                """Enable convert button if output name doesn't already exist"""
                ow_state = self.view.get_var("check_ow")
                if (not os.path.isfile(os.path.normpath(os.path.join(
                        self.view.output_dir,
                        filename_var.get() + ".sqlite"
                    )
                )) and filename_var.get() != "") or ow_state == True:
                    # fie does not exists yet
                    self.view.get_widget("convert_btn").configure(state="normal")
                    self.add_variable("filename_var", filename_var.get())
                else:
                    self.view.get_widget("convert_btn").configure(state="disabled")
                    # if invalid filename remove it from
                    if "filename_var" in self.view.variables:
                        del self.view.variables["filename_var"] 
                    

            # Add Entry widget to allow user to chose
            # another name for generated outputs
            filename_var = ctk.StringVar()
            filename_var.trace_add("write", callback_entry)

            filename_entry = ctk.CTkEntry(
                master=self.view.get_widget("conversion_frame"),
                textvariable=filename_var
            )
            filename_entry_gridoptions = {
                "row":1,
                "column":1
            }
            self.add_widget(
                widget=filename_entry,
                widget_name="filename_entry",
                widget_grid=filename_entry_gridoptions
            )

            def callback_cb(file):
                """callback on checkbox state change"""
                if check_ow.get() == "on":
                    self.view.get_widget("convert_btn").configure(state="normal")
                    self.add_variable("check_ow", True)
                elif check_ow.get() == "off" and (file.get() == "" or os.path.isfile(os.path.normpath(os.path.join(
                        self.view.output_dir,
                        filename_var.get() + ".sqlite"
                    ))
                )):
                    self.view.get_widget("convert_btn").configure(state="disabled")
                    self.view.variables["check_ow"] = False

            # Add checkbox for overwrite previous output option
            check_ow = ctk.StringVar()
            overwrite_cb = ctk.CTkCheckBox(
                master=self.view.get_widget("conversion_frame"),
                text="Overwrite existing file in output directory",
                variable=check_ow,
                command=lambda: callback_cb(filename_var),
                onvalue="on",
                offvalue="off"
            )
            overwrite_cb_gridoptions = {
                "row":1,
                "column":3
            }
            self.add_widget(
                widget=overwrite_cb,
                widget_name="overwrite_cb",
                widget_grid=overwrite_cb_gridoptions
            )

        else:
            self.view.get_widget("convert_btn").configure(state="normal")
    
    def convert(self):
        """Run conversion process based on user selection,
        ie: create database, erd and pdf
        """
        self.model.output_path = self.view.output_dir
        spreadsheet_name = os.path.splitext(os.path.basename(self.view.filepath))[0]
        ow_state = self.view.variables.get("check_ow")
        user_defined_filename = self.view.variables.get("filename_var")

        if ow_state == True and user_defined_filename:
            # overwrite the specified filename if exists
            try:
                os.remove(os.path.join(self.view.output_dir, user_defined_filename + ".sqlite"))
            except FileNotFoundError:
                pass
            self.model.convert(output_name=user_defined_filename)
        elif ow_state == True and user_defined_filename is None:
            os.remove(os.path.join(self.view.output_dir, spreadsheet_name + ".sqlite"))
            self.model.convert()
        elif ow_state != True and user_defined_filename:
            # create with specified filename without overwrite
            self.model.convert(output_name=user_defined_filename)
        elif ow_state != True and user_defined_filename is None:
            self.model.convert()
        
        self.view.show_success(msg="Your spreadsheet has been converted succesfully !")

    def display_pdf_from_sqlite(self):
        """Display a Generate PDF from sqlite button"""

        convert_btn = ctk.CTkButton(
            master=self.view.get_widget("conversion_frame"),
            text="Generate PDF",
            command=self.sqlite2pdf,
        )
        convert_btn_gridoptions = {
            "row":1,
            "column":0,
            "sticky": "nsew"
        }
        self.add_widget(
            widget=convert_btn,
            widget_name="convert_btn",
            widget_grid=convert_btn_gridoptions
        )

    def sqlite2pdf(self):
        """Run documentation creation from sqlite"""
        self.model.input_path = self.view.filepath
        self.model.output_path = self.view.output_dir
        try:
            self.model.sqlite2pdf()
        except Exception as e:
            logging.error(
                "An error occured during pdf creation: {}".format(str(e)),
                "\nPlease ensure you maintained metadata tables name, attributes and properties"
            )
        else:
            self.view.show_success(msg="Your pdf has been generated successfully !")

    def add_widget(self, widget, widget_name, widget_grid:dict):
        """Add widget to view"""

        self.view.add_widget(widget, widget_name, **widget_grid)

    def add_variable(self, var_name, value):
        """Add variable value to view for future access"""
        self.view.variables[var_name] = value
