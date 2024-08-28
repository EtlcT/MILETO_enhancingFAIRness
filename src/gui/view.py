import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from conf.config import META_TABLES

class View(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ss2db")
        self.controller = None
        self.createWidgets()
        self.additional_widgets = {}
        self.variables = {}

    def createWidgets(self):

        self.input_frame = ctk.CTkFrame(master=self)
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

        # from sqlite checkbox that enable to select sqlite file
        self.check_fsqlite = ctk.StringVar()
        self.from_sqlite_cb = ctk.CTkCheckBox(
            master = self.input_frame,
            text="generate pdf from existing sqlite",
            variable=self.check_fsqlite,
            onvalue="on",
            offvalue="off"
        )
        self.from_sqlite_cb.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
        )


    def set_controller(self, controller):
        self.controller = controller

    def browse_file(self):
        """Open a file dialog window for spreadsheets files
        then display selected file
        """
        self.variables["from_sqlite"] = self.check_fsqlite.get()
        if self.get_var("from_sqlite") == "off" or self.get_var("from_sqlite") == "":

            self.filepath = ctk.filedialog.askopenfilename(
                title="Select a file",
                initialdir=os.path.expanduser("~"),
                filetypes=[("All Excel files", "*.xlsx *.xls *.xlsm *.xlsb *.odf *.ods *.odt")]
            )

            if self.filepath:
                #delete previous content if exist
                self.clean_frame(mode="all")
                # display selected file in view input_frame
                self.selected_file()

                self.controller.spreadsheet_loader(self.filepath)
        
        else:
            self.filepath = ctk.filedialog.askopenfilename(
                title="Select a file",
                filetypes=[("sqlite File", "*.sqlite")]
            )
            
            if self.filepath:
                #delete previous content if exist
                self.clean_frame(mode="all")
                self.controller.display_conversion_frame()
    
    def selected_file(self):
        selected_file = ctk.CTkLabel(
            master=self.input_frame,
            text=self.filepath
        )
        selected_file.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=10,
            pady=(10, 0),
            sticky="w"
        )

    def display_spreadsheet_frame(self):
        """Create frame to display selected spreadsheet"""
        
        self.spreadsheet_frame = ctk.CTkFrame(
            master=self.input_frame
        )
        self.spreadsheet_frame.grid_columnconfigure(0, weight=1)
        self.spreadsheet_frame.grid(
            row=2,
            column=0,
            sticky="nsew"
        )

        # create treeview widget in spreadsheet_frame to display sheet
        self.sheet = ttk.Treeview(
            master=self.spreadsheet_frame
        )
        self.sheet.grid(
            row= 1,
            column=0,
            sticky="nsew"
        )

    def display_sheet_selector(self, tmp_data):
        """Add dropmenu for sheet selection to view"""
        
        table_list = list(tmp_data.keys())
        table_list.insert(0, "")

        def sheet_selection_callback(choice, tmp_data):
            """Callback function that display sheet corresponding
            to user selection in drop menu
            """
            self.sheet.delete(*self.sheet.get_children())
            if choice != "":
                self.display_sheet(tmp_data, choice)

        self.sheet_selection = ctk.CTkComboBox(
            master=self.spreadsheet_frame,
            values=table_list,
            command=lambda choice : sheet_selection_callback(choice, tmp_data)
        )
        self.sheet_selection.grid(
            row=0,
            column=0,
            sticky="w"
        )
    
    def display_sheet(self, tmp_data, selected_sheet):
        """Called on sheet_selector's changes
        Update treeview widget to display selected sheet
        """

        self.sheet["column"] = list(tmp_data[selected_sheet].columns)
        self.sheet["show"] = "headings"
        for column in self.sheet["columns"]:
            self.sheet.heading(column, text=column)
        
        df_rows = tmp_data[selected_sheet].head(20).to_numpy().tolist()
        for row in df_rows:
            self.sheet.insert("", "end", values=row)
        
        self.sheet.bind("<Button-1>", lambda event: self.controller.on_header_click(event, selected_sheet))

        if selected_sheet in META_TABLES:
            self.sheet.bind("<Button-1>", lambda event: self.controller.on_cell_click(event, selected_sheet))

    def display_upt_cell(self, value, x, y):
        """Display entry widget for changes in metadata table cell"""
        self.cell_entry = ctk.CTkEntry(self.sheet)
        self.cell_entry.insert(0, value)
        self.cell_entry.place(x=x,y=y)
        self.cell_entry.focus()
    
    def display_spreadsheet_option(self):
        """Display buttons to create and update metadata tables
        and finally check spreadsheet
        """
        self.ss_option_frame = ctk.CTkFrame(
            master=self.input_frame
        )
        self.ss_option_frame.grid(
            row=3,
            columnspan=2
        )
        self.display_create_metatable()
        self.display_update_metatable()
        self.display_check_spreadsheet()


    #TODO: add control on metadata table content ?
    def display_create_metatable(self):
        """Display Create metadata table if not exist button"""
        self.create_metatable_btn = ctk.CTkButton(
            master=self.ss_option_frame,
            text="Create metadata table\n(if not exist)",
            command=self.controller.create_missing_metatable
        )
        self.create_metatable_btn.grid(
            row=1,
            column=0
        )
    
    def display_update_metatable(self):
        """Display update metadata table button"""
        self.upt_metatable_btn = ctk.CTkButton(
            master=self.ss_option_frame,
            text="Update metadata tables",
            command=self.controller.upt_metatable,
            state="disabled"
        )
        self.upt_metatable_btn.grid(
            row=1,
            column=2
        )
    
    def display_check_spreadsheet(self):
        """Display check spreadsheet data button to check
        data consistency regarding template
        """
        self.check_btn = ctk.CTkButton(
            master=self.ss_option_frame,
            text="Check Spreadsheet data",
            command=self.controller.verify_spreadsheet,
            state="disabled"
        )
        self.check_btn.grid(
            row=1,
            column=3
        )

    def browse_outdir(self):
        """Open file dialog window to select output directory"""
        self.output_dir = ctk.filedialog.askdirectory(
            initialdir=os.path.expanduser("~")
        )

        if self.output_dir:

            if self.get_var("from_sqlite") == "off" or self.get_var("from_sqlite") == "":

                output_basename = os.path.normpath(
                    os.path.splitext(os.path.basename(self.filepath))[0]
                )

                # TODO rename following function
                self.controller.display_convert_option(output_basename)
            
            else:
                self.controller.display_pdf_from_sqlite()

    def opt_metadata(self):
        """Display button for creating/updating metadata"""
        
        create_meta_btn = ctk.CTkButton(
            master=self.input_frame,
            text="Create metadata table",
            state="normal",
            command=self.controller.create_missing_metatable
        )
        create_meta_btn.grid(

        )
        pass

    def show_success(self, msg):
        """ Open Window with success message"""
        CTkMessagebox(
            master=self,
            title="Success",
            message=msg,
            icon="check",
            option_1="OK"
        )

    def add_widget(self, widget, widget_name, **grid_option):
        """Add widget with provided grid option to view"""
        widget.grid(**grid_option)
        # add new widget to additional_widgets for future retrieving
        self.additional_widgets[widget_name] = widget
    
    def rm_widget(self, widget_name):
        """Remove widget from view and delete it from additional_widgets dict"""
        if widget_name in self.additional_widgets:
            self.additional_widgets.get(widget_name).destroy()
            del self.additional_widgets[widget_name]

    def get_widget(self, widget_name):
        """Retrieve widget created from controller"""
        return self.additional_widgets.get(widget_name)

    # def delete_elmt(self, widget_name):
    #     """Delete widget/frame and childrens"""

    #     to_del_obj = self.additional_widgets.get(widget_name)
    #     to_del_obj.delete(*to_del_obj.get_children())

    def get_var(self, var_name):
        """Return variable value from dict
        if key doesn't exist, return None
        """
        return self.variables.get(var_name, None)

    def clean_frame(self, mode="all"):
        """Remove frame/widget from view"""
        if mode=="all":
            self.rm_widget("selected_file")
            self.rm_widget("error_frame")
            self.rm_widget("spreadsheet_frame")
            self.rm_widget("check_btn")
            self.rm_widget("conversion_frame")
        else:
            pass