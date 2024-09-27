import os
import logging
import tkinter as tk
import customtkinter as ctk
import time
from CTkMessagebox import CTkMessagebox

from src.gui.view import View, DCTermsForm
from src.gui.model import Model
from src.extraction.check import InvalidData, InvalidTemplate
from src.utils.utils import save_spreadsheet
from src.utils.utils_gui import get_authorized_type, CenterWindowToDisplay
from conf.config import *

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.dc_form_window = None

    def spreadsheet_loader(self, spreadsheet_path):
        """Display path to selected spreadsheet and load it
        Display button to check data validity
        """

        # load excel
        tmp_data = self.load_spreadsheet(spreadsheet_path)

        # create metadata tables if not exist
        missing_table = self.create_missing_metatable()

        # display option on spreadsheet (update, check)
        self.view.display_spreadsheet_option()

        # create spreadsheet frames
        self.view.create_spreadsheet_frame()

        # display dropmenu
        if missing_table:
            self.view.display_sheet_selector(self.model.tmp_data)
        else:
            self.view.display_sheet_selector(tmp_data)

    def load_spreadsheet(self, spreadsheet_path):
        """Load spreadsheet data"""
        self.model.input_path = spreadsheet_path
        tmp_data = self.model.load_spreadsheet(spreadsheet_path)
        return tmp_data

    def on_header_click(self, event, selected_sheet):
        """Allow modifying headers/column value on click"""
        region = self.view.data_sheet.identify("region", event.x, event.y)
        if region == "heading":
            # user click on some header
            column_id = self.view.data_sheet.identify_column(event.x)
            # Get the current heading text
            current_heading = self.view.data_sheet.heading(column_id)['text']

            # open dialog to ask for new heading value
            new_heading_window = self.view.open_edition_window(region, current_heading)
            new_heading_window.bind("<<ConfirmClick>>", lambda e: on_confirm())
            new_heading_window.bind("<<CancelClick>>", lambda e: on_cancel())
            
            def on_confirm():
            # If a new heading was provided, update the column heading
                new_heading = new_heading_window.new_value.get()
                # update treeview
                self.view.data_sheet.heading(column_id, text=new_heading)
                # update dataframe
                self.model.header_change(
                    selected_sheet, current_heading, new_heading)
                # refresh metadata
                self.refresh_meta()
                # store info that a change occurs
                self.view.variables["change_occurs"] = True
                new_heading_window.destroy()
    
            def on_cancel():
                new_heading_window.destroy()

    def on_cell_click(self, event, selected_sheet):
        """allow editing metadata tables fields that need to be filled
        by the researcher
        """

        region = self.view.meta_sheet.identify("region", event.x, event.y)
        if region == "cell":
            # user click on some cell
            row_idx = self.view.meta_sheet.identify_row(event.y)
            col_idx = int(self.view.meta_sheet.identify_column(event.x)[1:]) - 1
            cell_value = self.view.meta_sheet.item(row_idx)['values'][col_idx]
            col_name = self._get_meta_col_name(selected_sheet, col_idx)

            if self.is_editable_col(selected_sheet, col_idx) == True:
                # user has permission to edit this field
                match col_name:
                    # based on colunm, different variable are passed to view
                    case "expectedType":
                        # pass content of neighbor cell ie. inferred type
                        current_type = self.view.meta_sheet.item(row_idx)['values'][col_idx - 1]
                        authorized_conversion_type = get_authorized_type(current_type)
                        if authorized_conversion_type is not None:
                            new_cell_window = self.view.open_edition_window(region, cell_value, selected_sheet, col_name, authorized_conversion_type)
                    case "referenceTable":
                        # pass list of data table name
                        datatable_list = [_ for _ in self.model.tmp_data.keys() if _ not in META_TABLES]
                        datatable_list.insert(0, "")
                        new_cell_window = self.view.open_edition_window(region, cell_value, selected_sheet, col_name, datatable_list)
                    case _:
                        new_cell_window = self.view.open_edition_window(region, cell_value, selected_sheet, col_name)
                        
                new_cell_window.bind("<<ConfirmClick>>", lambda e: on_confirm())
                new_cell_window.bind("<<CancelClick>>", lambda e: on_cancel())

                def on_confirm():
                    # If a new value was provided, update the cell
                    # store info that a change occurs
                    self.view.variables["change_occurs"] = True
                    if isinstance(new_cell_window.new_value, ctk.CTkTextbox):
                        new_cell = new_cell_window.new_value.get("0.0", "end")
                    else:
                        new_cell = new_cell_window.new_value.get()
                    self.update_cell_value(new_cell, selected_sheet, row_idx, col_idx)
                    new_cell_window.destroy()
    
            def on_cancel():
                new_cell_window.destroy()

    def _get_meta_col_name(self, metatable_name, column_index):
        """Retrieve metadata table's column name from its index"""
        return self.model.tmp_data[metatable_name].columns[column_index]
    
    def edit_dc_terms(self):
        """Display a frame to edit datacite terms, if already open,
        focus on it
        """
        if (self.dc_form_window is None) or (not self.dc_form_window.winfo_exists()):
            self.dc_form_window = DCTermsForm(self, self.model.tmp_data[METAREF])
        else:
            self.dc_form_window.focus()


    def get_entries(self, entries):

        self.view.variables["change_occurs"] = True
        values = {}
        for object_name, content in entries.items():
            match DC_JSON_OBJECT[object_name]["type"]:
                case "object" :
                    values[object_name] = {}
                    for term, entry in content.items():
                        if isinstance(entry, dict):
                            values[object_name][term] = []
                            for idx, sub_entry_dict in entry.items():
                                sub_dict = {}
                                for sub_term, sub_entry in sub_entry_dict.items():
                                    sub_dict[sub_term] = sub_entry[0].get()
                                values[object_name][term].append(sub_dict)
                        else:
                            values[object_name][term] = entry[0].get()
                case "list":
                    values[object_name] = []
                    for occurrence, occurrence_details in content.items():
                        occurrence_dict = {}
                        for term, value in occurrence_details.items():
                            if isinstance(value, dict):
                                occurrence_dict[term] = []
                                for idx, sub_entry_dict in value.items():
                                    sub_dict = {}
                                    for sub_term, sub_entry in sub_entry_dict.items():
                                        sub_dict[sub_term] = sub_entry[0].get()
                                    occurrence_dict[term].append(sub_dict)
                            else:
                                if type(value[0]) == ctk.CTkTextbox:
                                    occurrence_dict[term] = value[0].get("0.0", "end")
                                else:
                                    occurrence_dict[term] = value[0].get()
                        values[object_name].append(occurrence_dict)
                case _:
                    for term, entry in content.items():
                        values[object_name] = entry[0].get()

        self.model.process_meta_dc_terms(values)
        self.refresh_meta()
        self.view.show_success("Metadata correctly added to meta_dc_terms table!\nYou can close this window")

    def refresh_meta(self):
        """Update metadata treeview on changes"""

        selected_meta_sheet = self.view.meta_sheet_selector.get()
        if selected_meta_sheet != "Select a sheet":
            self.view.meta_sheet.delete(*self.view.meta_sheet.get_children())
            df_rows = self.model.tmp_data[selected_meta_sheet].to_numpy().tolist()
            for row in df_rows:
                self.view.meta_sheet.insert("", "end", values=row)

    def is_editable_col(self, selected_sheet, col_idx):
        """Check if the user is allowed to modify value in the column
        he/she try to select in metadata tables

        This function prevent the user to modify unwanted value like
        Datacite metadata properties name for instance
        """

        if col_idx == 0 or (col_idx in [1, 2] and selected_sheet == INFO):
            auth = False
        else:
            auth = True

        return auth

    def update_cell_value(self, new_value, table, item, col):
        """Update treeview and dataframe"""
        # update treeview
        self.view.meta_sheet.set(item, col, new_value)

        # update dataframe
        row = self.view.meta_sheet.index(item)
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
            self.view.display_errors(str(e), error_type="data")
        except InvalidTemplate as e:
            self.view.display_errors(str(e), error_type="template")
        else:
            self.view.show_success("Valid spreadsheet provided")
            self.view.display_conversion_frame()

    def save_changes(self):
        """Open a asksaveasfile filedialog to save changes
        applied to spreadsheet
        """
        file = tk.filedialog.asksaveasfile(
            filetypes=[("OpenDocument Spreadsheet", "*.ods"),
                       ("Excel Workbook", "*.xlsx")],
            defaultextension=".xlsx",
            confirmoverwrite=True,
        )
        if file:
            file_format = file.name.split('.')[-1] if '.' in file.name else None
            save_spreadsheet(self.model.tmp_data, file.name, format=file_format)
            del self.view.variables["change_occurs"]
            # store saved spreadsheet filename to check for pending changes later
            self.view.variables["saved_spreadsheet"] = file.name
            
    def convert(self):
        """Run conversion process based on user selection,
        ie: create database, erd and pdf
        """
        self.model.output_path = self.view.output_dir
        spreadsheet_name = os.path.splitext(
            os.path.basename(self.view.filepath))[0]
        ow_state = self.view.variables.get("check_ow")
        user_defined_filename = self.view.variables.get("filename_var")

        if ow_state == True and user_defined_filename:
            # overwrite the specified filename if exists
            try:
                os.remove(os.path.join(self.view.output_dir,
                          user_defined_filename + ".sqlite"))
            except FileNotFoundError:
                pass
            self.model.convert(output_name=user_defined_filename)
        elif ow_state == True and user_defined_filename is None:
            try:
                os.remove(os.path.join(self.view.output_dir,
                          spreadsheet_name + ".sqlite"))
            except FileNotFoundError:
                pass
            self.model.convert()
        elif ow_state != True and user_defined_filename:
            # create with specified filename without overwrite
            self.model.convert(output_name=user_defined_filename)
        elif ow_state != True and user_defined_filename is None:
            self.model.convert()

        self.view.show_success(
            msg="Your spreadsheet has been converted succesfully !")
        self.view.clean_stage(mode="all")

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
            self.view.show_success(
                msg="Your pdf has been generated successfully !")
            self.view.clean_stage()

    def create_missing_metatable(self):
        """Check if metadata tables are missing"""
        missing_table = self.model.create_missing_metatable()
        return missing_table
    
    # TODO
    def upt_metatable(self):
        pass

    def on_closing(self):
        """Handle window close event to prevent user from loosing
        pending changes
        """
        if self.view.get_var("change_occurs"):
            # changes have been detected
                msg_exit_box = self.view.warning_exit()
                if msg_exit_box.get() == "Quit without saving":
                    self.view.destroy()
                elif msg_exit_box.get() == "Yes, save spreadsheet":
                    self.save_changes()
        else:
            self.view.destroy()

        return