import os
import logging
from tkinter import ttk
import customtkinter as ctk

from src.gui.view import View
from src.gui.model import Model
from src.extraction.check import InvalidData
from src.utils.utils import output_exist
from conf.config import *

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

        # display dropmenu
        self.view.display_sheet_selector(tmp_data)
        
        # display option on spreadsheet (update, check)
        self.view.display_spreadsheet_option()

        # create metadata tables if not exist
        self.create_missing_metatable()

    def load_spreadsheet(self, spreadsheet_path):
        """Load spreadsheet data"""
        self.model.input_path = spreadsheet_path
        tmp_data = self.model.load_spreadsheet(spreadsheet_path)
        return tmp_data
 
    def on_header_click(self, event, selected_sheet):
        """Allow modifying headers/column value on click"""
        region = self.view.sheet.identify("region", event.x, event.y)
        if region == "heading":
            # user click on some header
            column_id = self.view.sheet.identify_column(event.x)
            # Get the current heading text
            current_heading = self.view.sheet.heading(column_id)['text']
        
            # open dialog to ask for new heading value
            new_heading = ctk.CTkInputDialog(
                text=f"Enter new heading for '{current_heading}':",
                title="Edit column name"
            )

            # If a new heading was provided, update the column heading
            if new_heading:
                new_value = new_heading.get_input()
                self.view.sheet.heading(column_id, text=new_value)
                self.model.header_change(selected_sheet, current_heading, new_value)

    def on_cell_click(self, event, selected_sheet):
        """allow editing metadata tables fields that need to be filled
        by the researcher
        """

        region = self.view.sheet.identify("region", event.x, event.y)
        if region == "cell":
            # user click on some cell
            selected_item = self.view.sheet.identify_row(event.y)
            selected_column = self.view.sheet.identify_column(event.x)
            column_index = int(selected_column[1:]) - 1
            cell_value = self.view.sheet.item(selected_item)['values'][column_index]

            if self.is_editable_col(selected_sheet, column_index) == True:
                # user has permission to edit this field
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
    
    def is_editable_col(self, selected_sheet, col_idx):
        """Check if the user is allowed to modify value in the column
        he/she try to select in metadata tables

        This function prevent the user to modify unwanted value like
        Datacite metadata properties name for instance
        """

        if col_idx == 0 or (col_idx in [1,2] and selected_sheet==INFO):
            auth = False
        else:
            auth = True

        return auth

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
        self.view.rm_frame("error_frame")
        self.view.rm_frame("conversion_frame")

        try:
            self.model.verify_spreadsheet()
        except InvalidData as e:
            self.view.display_errors(str(e).replace("str: ", ""))
        # TODO catch other type of exception
        else:
            self.view.show_success("Valid spreadsheet provided")
            self.view.display_conversion_frame()
    
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
            try:
                os.remove(os.path.join(self.view.output_dir, spreadsheet_name + ".sqlite"))
            except FileNotFoundError:
                pass
            self.model.convert()
        elif ow_state != True and user_defined_filename:
            # create with specified filename without overwrite
            self.model.convert(output_name=user_defined_filename)
        elif ow_state != True and user_defined_filename is None:
            self.model.convert()
        
        self.view.show_success(msg="Your spreadsheet has been converted succesfully !")
        self.view.clean_frame(mode="all")

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
            self.view.rm_frame("spreadsheet_frame")
            self.view.rm_frame("error_frame")
            self.view.rm_frame("conversion_frame")
            self.view.rm_widget("check_btn")

    def add_widget(self, widget, widget_name, widget_grid:dict):
        """Add widget to view"""

        self.view.add_widget(widget, widget_name, **widget_grid)

    def create_missing_metatable(self):
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