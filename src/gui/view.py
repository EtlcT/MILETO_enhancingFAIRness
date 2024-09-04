import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

from conf.config import META_TABLES
from src.utils.utils import resource_path, output_exist
from src.utils.utils_gui import get_str_max_length
from conf.view_config import *

class View(ctk.CTk):
    def __init__(self):
        super().__init__()
        #ctk.set_appearance_mode("light")
        self.title("Ss2db")
        self.controller = None
        self.createWidgets()
        self.additional_frames = {}
        self.additional_widgets = {}
        self.variables = {}

    def createWidgets(self):


        self.welcome_label = ctk.CTkLabel(
            master=self,
            text="Welcome into Spreadsheet to SQLite converter !",
            font=TITLE_FONT
        )
        self.welcome_label.grid(
            row=0,
            column=0,
            pady=(20,20),
            sticky="nsew"
        )

        self.input_frame = ctk.CTkFrame(master=self)
        self.input_frame.grid(
            row=2,
            column=0,
            **FRAME_GRID
        )
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_label = ctk.CTkLabel(
            master=self,
            text="Input selection",
            font=SUBTITLE_FONT
        )
        self.input_label.grid(
            row=1,
            column=0,
            **SUBTITLE_GRID
        )
        self.input_frame.grid_columnconfigure(0,weight=1)

        # display instruction to user: chose spreadsheet
        self.browse_file_label = ctk.CTkLabel(
            master=self.input_frame,
            text="Select a spreadsheet to convert into sqlite database",
            font=TEXT_FONT
        )
        self.browse_file_label.grid(
            row=0,
            column=0,
            **LABEL_GRID
        )
        
        # browse button open file dialog
        self.browse_file_btn = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            command=self.browse_file,
            font=TEXT_FONT
        )
        self.browse_file_btn.grid(
            row=0,
            column=1,
            sticky="w",
            **BUTTON_GRID
        )

        # from sqlite checkbox that enable to select sqlite file
        self.check_fsqlite = ctk.StringVar()
        self.from_sqlite_cb = ctk.CTkCheckBox(
            master = self.input_frame,
            text="generate pdf from existing sqlite",
            font=TEXT_FONT,
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
                self.display_selected_file()

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
    
    def display_selected_file(self):

        self.selected_file = ctk.CTkLabel(
            master=self.input_frame,
            text=self.filepath,
            font=TEXT_FONT
        )
        self.selected_file.grid(
            row=1,
            column=0,
            columnspan=3,
            **LABEL_GRID
        )
        self.add_widget("selected_file", self.selected_file)

    def display_spreadsheet_frame(self):
        """Create frame to display selected spreadsheet"""

        #* Style treeview table 
        style = ttk.Style()
        style.theme_use("default")
        if ctk.get_appearance_mode() == "Dark":
            style.configure("Treeview",**DARK_TV_CONFIG)
            style.map('Treeview', background=[('selected', '#22559b')])
            style.configure("Treeview.Heading", **DARK_TVH_CONFIG)
            style.map("Treeview.Heading",
                    background=[('active', '#3484F0')]
            )

        self.spreadsheet_frame = ctk.CTkFrame(
            master=self.input_frame
        )
        self.spreadsheet_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew"
        )
        self.spreadsheet_frame.grid_columnconfigure(0, weight=1)
        self.add_frame("spreadsheet_frame", self.spreadsheet_frame)

        self.xscroll = ttk.Scrollbar(
            self.spreadsheet_frame,
            orient="horizontal"
        )
        self.xscroll.grid(
            row=2,
            column=0,
            sticky="we",
            columnspan=2
        )

        # create treeview widget in spreadsheet_frame to display sheet
        self.sheet = ttk.Treeview(
            master=self.spreadsheet_frame,
            xscrollcommand=self.xscroll.set
        )
        self.sheet.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(10,0),
            pady=(0,10),
        )

        self.xscroll.configure(command=self.sheet.xview)

    def display_sheet_selector(self, tmp_data):
        """Add dropmenu for sheet selection to view"""
        
        table_list = list(tmp_data.keys())
        table_list.insert(0, "Select a sheet")

        def sheet_selector_callback(choice, tmp_data):
            """Callback function that display sheet corresponding
            to user selection in drop menu
            """
            self.sheet.delete(*self.sheet.get_children())
            if choice != "Select a sheet":
                self.display_sheet(tmp_data, choice)

        self.sheet_selector = ctk.CTkComboBox(
            master=self.spreadsheet_frame,
            values=table_list,
            command=lambda choice : sheet_selector_callback(choice, tmp_data),
            font=TEXT_FONT,
            width=get_str_max_length(table_list)*8,

        )
        self.sheet_selector.grid(
            row=0,
            column=0,
            padx=(10, 0),
            pady=(20,20),
            sticky="w",
        )
    
    def display_sheet(self, tmp_data, selected_sheet):
        """Called on sheet_selector's changes
        Update treeview widget to display selected sheet
        """

        self.sheet["column"] = list(tmp_data[selected_sheet].columns)
        self.sheet["show"] = "headings"
        for column in self.sheet["columns"]:
            self.sheet.heading(column, text=column)
        
        df_rows = tmp_data[selected_sheet].to_numpy().tolist()
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
        # self.ss_option_frame = ctk.CTkFrame(
        #     master=self.input_frame
        # )
        # self.ss_option_frame.grid(
        #     row=3,
        #     columnspan=2
        # )
        # self.add_frame("ss_option_frame", self.ss_option_frame)

        self.display_check_spreadsheet()


    #TODO: add control on metadata table content ?

    
    def display_check_spreadsheet(self):
        """Display check spreadsheet data button to check
        data consistency regarding template
        """
        self.check_btn = ctk.CTkButton(
            master=self.input_frame,
            text="Check Spreadsheet data",
            font=TEXT_FONT,
            command=self.controller.verify_spreadsheet
        )
        self.check_btn.grid(
            row=3,
            column=0,
            columnspan=2,
            **BUTTON_GRID
        )
        self.add_widget("check_btn", self.check_btn)

    def display_errors(self, error_msg):
        """Display frame to show error find during spreadsheet check"""

        self.error_frame = ctk.CTkFrame(master=self.input_frame)
        self.error_frame.grid(
            row=4,
            column=0,
            columnspan=2
        )

        self.add_frame("error_frame", self.error_frame)

        self.error_icon_img = ctk.CTkImage(
            light_image= Image.open(os.path.normpath(resource_path("src/gui/assets/error.png"))),
            size=(40,40)
        )
        self.error_icon = ctk.CTkLabel(
            master=self.error_frame,
            image=self.error_icon_img,
            text=""
        )
        self.error_icon.grid(
            row=0,
            column=0
        )
        self.errors = ctk.CTkLabel(
            master=self.error_frame,
            text=error_msg,
            justify="left",
            font=TEXT_FONT
        )
        self.errors.grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

    #TODO radio button only sqlite and erd OR all
    def display_conversion_frame(self):
        """Add a conversion frame to view with:
        - browse folder button for output directory selection
        - conversion option radio buttons
        (generate all, only sqlite and erd)
        """

        self.conversion_frame_label = ctk.CTkLabel(
            master=self,
            text="Conversion options",
            font=SUBTITLE_FONT
        )
        self.conversion_frame_label.grid(
            row=3,
            column=0,
            **SUBTITLE_GRID
        )
        self.add_widget("conversion_frame_label", self.conversion_frame_label)

        self.conversion_frame = ctk.CTkFrame(master=self)
        self.conversion_frame.grid_columnconfigure(0, weight=1)
        self.conversion_frame.grid(
            row=4,
            column=0,
            **FRAME_GRID
        )
        self.add_frame("conversion_frame", self.conversion_frame)

        self.outdir_label = ctk.CTkLabel(
            master=self.conversion_frame,
            text="Select a directory to store outputs",
            font=TEXT_FONT
        )
        self.outdir_label.grid(
            row=0,
            column=0,
            **LABEL_GRID
        )

        self.outdir_btn = ctk.CTkButton(
            master=self.conversion_frame,
            command=self.browse_outdir,
            text="Browse Folder",
            font=TEXT_FONT
        )
        self.outdir_btn.grid(
            row=0,
            column=1,
            **BUTTON_GRID
        )

    def browse_outdir(self):
        """Open file dialog window to select output directory"""

        self.rm_filename_var()

        self.output_dir = ctk.filedialog.askdirectory(
            initialdir=os.path.expanduser("~")
        )

        if self.output_dir:
            if self.get_var("from_sqlite") == "on":
                self.sqlite2pdf_btn()
            else:
                output_basename = os.path.normpath(
                    os.path.splitext(os.path.basename(self.filepath))[0]
                )

                self.display_convert_btn()

                if output_exist(self.output_dir, output_basename):
                    # an output already exists for this spreadsheet
                    # Add warning message to conversion_frame ask user how to handle existing files
                    self.display_file_exist_warning()
                else:
                    self.convert_btn.configure(state="normal")
                self.filename_entry(output_basename)
                self.ow_checkbox()

        
    def filename_entry(self, output_basename):
        """Add Entry widget to allow user to chose
        another name for generated outputs
        """
        def callback_entry(*args):
            """Enable convert button if output name doesn't already exist
            or if overwrite option is checked
            """
            ow_state = self.get_var("check_ow")
            if (output_exist(self.output_dir, self.filename_var.get()) == False
                and self.filename_var.get() != "") or ow_state == True:
                # fie does not exists yet
                self.convert_btn.configure(state="normal")
                self.add_variable("filename_var", self.filename_var.get())
            else:
                self.convert_btn.configure(state="disabled")
                # if invalid filename remove it from
                self.rm_filename_var()

        self.filename_var = ctk.StringVar(
            value=output_basename
        )
        self.filename_var.trace_add("write", callback_entry)

        filename_entry = ctk.CTkEntry(
            master=self.conversion_frame,
            textvariable=self.filename_var,
            font=TEXT_FONT,
            width=(get_str_max_length(self.filename_var.get()) + 15)*8
        )
        filename_entry.grid(
            row=1,
            column=1,
        )
    
    def ow_checkbox(self):
        """Add checkbox for overwrite previous output option"""

        def callback_cb(file):
            """callback on checkbox state change"""
            if self.check_ow.get() == "on":
                self.convert_btn.configure(state="normal")
                self.add_variable("check_ow", True)
            elif self.check_ow.get() == "off":
                self.variables["check_ow"] = False
                if (file == "" or output_exist(self.output_dir, file)):
                    self.convert_btn.configure(state="disabled")

        self.check_ow = ctk.StringVar()
        self.overwrite_cb = ctk.CTkCheckBox(
            master=self.conversion_frame,
            text="Overwrite existing file in output directory",
            variable=self.check_ow,
            command=lambda: callback_cb(self.filename_var.get()),
            onvalue="on",
            offvalue="off"
        )
        self.overwrite_cb.grid(
            row=1,
            column=3
        )
    

    def display_convert_btn(self):
        """Display convert button to run sqlite, erd and pdf creation"""

        self.convert_btn = ctk.CTkButton(
            master=self.conversion_frame,
            text="Convert spreadsheet",
            command=self.controller.convert,
            state="disabled",
            font=TEXT_FONT
        )
        self.convert_btn.grid(
            row=2,
            column=0,
            columnspan=2,
            **BUTTON_GRID
        )

    def display_file_exist_warning(self):
        """Display warning if file(s) already exist"""

        self.file_exists_warning_msg = ( 
            f"WARNING: Output(s) already exist in output directory for this spreadsheet"
            "\nCheck the overwrite checkbox to delete existing file(s)"
            " or provide another filename: "
        )
        self.file_exists_warning = ctk.CTkLabel(
            master=self.conversion_frame,
            text=self.file_exists_warning_msg,
            font=TEXT_FONT,
            text_color="#960000"
        )
        self.file_exists_warning.grid(
            row=1,
            column=0
        )

    def sqlite2pdf_btn(self):
        """Display a Generate PDF from sqlite button"""

        self.generate_btn = ctk.CTkButton(
            master=self.conversion_frame,
            text="Generate PDF",
            command=self.controller.sqlite2pdf,
        )
        self.generate_btn.grid(
            row=1,
            column=0,
            **BUTTON_GRID
        )

    def show_success(self, msg):
        """ Open Window with success message"""
        CTkMessagebox(
            master=self,
            title="Success",
            message=msg,
            icon="check",
            option_1="OK"
        )

    def add_frame(self, frame_name, frame):
        """Add new widget to additional_frames for future retrieving"""
        self.additional_frames[frame_name] = frame
    
    def add_widget(self, widget_name, widget):
        """Add new widget to additional_frames for future retrieving"""
        self.additional_widgets[widget_name] = widget
    
    def rm_frame(self, frame_name):
        """Remove frame from view if exist"""
        if frame_name in self.additional_frames:
            frame = self.get_frame(frame_name)
            frame.destroy()
    
    def rm_widget(self, widget_name):
        """Remove frame from view if exist"""

        if widget_name in self.additional_widgets:
            widget = self.get_widget(widget_name)
            widget.destroy()

    def get_frame(self, frame_name):
        """Retrieve widget created from controller"""
        return self.additional_frames.get(frame_name)
    
    def get_widget(self, widget_name):
        """Retrieve widget created from controller"""
        return self.additional_widgets.get(widget_name)
    
    def add_variable(self, var_name, value):
        """Add variable value to view for future access"""
        self.variables[var_name] = value

    def get_var(self, var_name):
        """Return variable value from dict
        if key doesn't exist, return None
        """
        return self.variables.get(var_name, None)

    def clean_frame(self, mode="all"):
        """Remove frame/widget from view"""
        if mode=="all":
            self.rm_widget("selected_file")
            self.rm_frame("error_frame")
            self.rm_frame("spreadsheet_frame")
            self.rm_widget("check_btn")
            self.rm_widget("conversion_frame_label")
            self.rm_frame("conversion_frame")
        else:
            pass
    
    def rm_filename_var(self):
        """Remove previous filename variable if exist"""
        if "filename_var" in self.variables:
            del self.variables["filename_var"]
    
    