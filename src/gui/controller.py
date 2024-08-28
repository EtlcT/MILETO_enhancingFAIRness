import os
import logging
from tkinter import ttk
import customtkinter as ctk
from PIL import Image

from src.gui.view import View
from src.gui.model import Model
from src.extraction.check import InvalidData
from src.utils.utils import resource_path, output_exist
from conf.config import META_TABLES

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

        # load excel
        tmp_data = self.load_spreadsheet(spreadsheet_path)

        # display spreadsheet and dropmenu for sheet selection
        self.view.display_spreadsheet_frame()
        # create logs to track changes in spreadsheet
        self.model.create_logs()
        # display dropmenu
        self.view.display_sheet_selector(tmp_data)

        # display option on spreadsheet (create, update, check)
        self.view.display_spreadsheet_option()

    def load_spreadsheet(self, spreadsheet_path):
        """Load spreadsheet data"""
        self.model.input_path = spreadsheet_path
        tmp_data = self.model.load_spreadsheet(spreadsheet_path)
        return tmp_data
 
    def on_header_click(self, event, selected_sheet):
        """Allow modifying headers value on click"""
        region = self.view.sheet.identify("region", event.x, event.y)
        if region == "heading":
            # user click on some header
            column_id = self.view.sheet.identify_column(event.x)
            # Get the current heading text
            current_heading = self.view.sheet.heading(column_id)['text']
        
            # open dialog to ask for new heading value
            new_heading = ctk.CTkInputDialog(text=f"Enter new heading for '{current_heading}':")
        
            # If a new heading was provided, update the column heading
            if new_heading:
                self.view.sheet.heading(column_id, text=new_heading.get_input())
                self.view.upt_metatable_btn.configure(state="normal")
                self.model.upt_change_log(selected_sheet, current_heading, new_heading)

    def on_cell_click(self, event, selected_sheet):
        """allow modifying"""
        global entry
        region = self.view.sheet.identify("region", event.x, event.y)
        if region == "cell":
            # user click on some cell
            selected_item = self.view.sheet.identify_row(event.y)
            selected_column = self.view.sheet.identify_column(event.x)
            column_index = int(selected_column[1:]) - 1
            cell_value = self.view.sheet.item(selected_item)['values'][column_index]

            bbox = self.view.sheet.bbox(selected_item, selected_column)
            x=bbox[0]
            y=bbox[1]
        
            # Create an Entry widget and place it at the cell position
            self.view.display_upt_cell(cell_value,x,y)
            self.view.cell_entry.bind(
                '<Return>',
                lambda event: self.update_cell_value(
                    event,
                    selected_sheet,
                    selected_item,
                    column_index
                )
            )

    def update_cell_value(self, event, table, item, col):
        """Update treeview and dataframe"""
        # update treeview
        new_value = self.view.cell_entry.get()
        self.view.sheet.set(item, col, new_value)

        # delete existing entry
        self.view.cell_entry.destroy()

        # update dataframe
        row = self.view.sheet.index(item)
        self.model.upt_cell(table, row, col, new_value)


    def verify_spreadsheet(self):
        """Control spreadsheet is conform
        if not display errors
        else display browse directory for output and convert button
        """

        # remove previous errors
        self.view.rm_widget("error_frame")
        self.view.rm_widget("conversion_frame")

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

    def display_convert_option(self, output_basename):
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

        if output_exist(self.view.output_dir, output_basename):
            # an output already exists for this spreadsheet

            # Add warning message to error_frame ask user how to handle existing files
            file_exists_warning_msg = ( 
                f"WARNING: Output(s) already exist in output directory for this spreadsheet"
                "\nCheck the overwrite checkbox to delete existing file(s)"
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

        else:
            self.view.get_widget("convert_btn").configure(state="normal")

        def callback_entry(*args):
            """Enable convert button if output name doesn't already exist"""
            ow_state = self.view.get_var("check_ow")
            if (output_exist(self.view.output_dir, filename_var.get()) == False
                and filename_var.get() != "") or ow_state == True:
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
        filename_var = ctk.StringVar(
            value=output_basename
        )
        filename_var.trace_add("write", callback_entry)

        filename_entry = ctk.CTkEntry(
            master=self.view.get_widget("conversion_frame"),
            textvariable=filename_var,

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
            elif check_ow.get() == "off":
                self.view.variables["check_ow"] = False
                if (file == "" or output_exist(self.view.output_dir, file)):
                    self.view.get_widget("convert_btn").configure(state="disabled")

        # Add checkbox for overwrite previous output option
        check_ow = ctk.StringVar()
        overwrite_cb = ctk.CTkCheckBox(
            master=self.view.get_widget("conversion_frame"),
            text="Overwrite existing file in output directory",
            variable=check_ow,
            command=lambda: callback_cb(filename_var.get()),
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
        self.view.clean_frame(mode="all")

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
            self.view.rm_widget("selected_file")
            self.view.rm_widget("spreadsheet_frame")
            self.view.rm_widget("error_frame")
            self.view.rm_widget("conversion_frame")
            self.view.rm_widget("check_btn")

    def add_widget(self, widget, widget_name, widget_grid:dict):
        """Add widget to view"""

        self.view.add_widget(widget, widget_name, **widget_grid)

    def add_variable(self, var_name, value):
        """Add variable value to view for future access"""
        self.view.variables[var_name] = value

    def create_metatable(self):
        """Check if metadata tables are missing"""
        missing_table = self.model.create_missing_metatable()
        if missing_table:
            # metadata table has been added, refresh treeview
            self.view.spreadsheet_frame.destroy()
            self.view.display_spreadsheet_frame()
            self.view.display_sheet_selector(self.model.tmp_data)
            self.view.check_btn.configure(state="normal")
    #TODO
    def upt_metatable(self):
        pass