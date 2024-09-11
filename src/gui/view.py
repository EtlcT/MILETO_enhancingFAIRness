import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

from conf.config import *
from src.utils.utils import resource_path, output_exist
from src.utils.utils_gui import *
from conf.view_config import *


class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Modify content")
        self.after(10, self.lift) # force focus on toplevel window
    
    def edit_head_and_cell(self, *args):
        """top level window that allow user to modify header and cell content"""

        self.label = ctk.CTkLabel(
            master=self,
            text=f"Enter new {args[0]} value: ",
            font=TEXT_FONT
        )
        self.label.pack(
            **LABEL_OPT
        )

        if args[0] == "header":
            self.geometry(CenterWindowToDisplay(self, 500, 150, self._get_window_scaling()))
            self.txt_var = ctk.StringVar(value=args[1])
            self.new_value = ctk.CTkEntry(
                master=self,
                textvariable=self.txt_var,
                font=TEXT_FONT
            )
            self.new_value.pack(
                **LABEL_OPT
            )
        else:
            self.geometry(CenterWindowToDisplay(self, 500, 350, self._get_window_scaling()))
            self.new_value = ctk.CTkTextbox(
                master=self,
                wrap="word"
            )
            self.new_value.insert("0.0", args[1])
            self.new_value.pack(
                anchor="center",
                padx=10,
                pady=10,
                fill="both"
            )
        self.btn_frame = ctk.CTkFrame(
            master=self
        )
        self.btn_frame.pack()
        self.valid_btn = ctk.CTkButton(
            master=self.btn_frame,
            text="Confirm change",
            command=self.on_confirm,
            font=TEXT_FONT
        )
        self.valid_btn.pack(
            side="left",
            anchor="center",
            **BUTTON_OPT
        )
        self.cancel_btn = ctk.CTkButton(
            master=self.btn_frame,
            text="Cancel change",
            command=self.on_cancel,
            font=TEXT_FONT
        )
        self.cancel_btn.pack(
            side="left",
            anchor="center",
            **BUTTON_OPT
        )
        
    def on_confirm(self):
        self.event_generate("<<ConfirmClick>>")
    
    def on_cancel(self):
        self.event_generate("<<CancelClick>>")

class View(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ss2db")
        self.controller = None
        self.createWidgets()
        self.additional_frames = {}
        self.additional_widgets = {}
        self.variables = {}
        self.protocol("WM_DELETE_WINDOW",lambda: self.controller.on_closing())

    def createWidgets(self):

        self.main_frame = ctk.CTkScrollableFrame(
            self
        )
        self.main_frame.pack(
            expand=True,
            fill="both"
        )

        self.toplevel_window = None

        self.welcome_label = ctk.CTkLabel(
            master=self.main_frame,
            text="Welcome into Spreadsheet to SQLite converter !",
            font=TITLE_FONT
        )
        self.welcome_label.pack(
            side="top",
            pady=(20,20),
            anchor="center"
        )

        self.input_label = ctk.CTkLabel(
            master=self.main_frame,
            text="Input selection",
            font=SUBTITLE_FONT
        )
        self.input_label.pack(
            side="top",
            padx=(10,0),
            pady=(10,0),
            anchor="w"
        )

        # radio button to chose spreadsheet conversion or sqlite processing
        self.input_radio_frame = ctk.CTkFrame(
            master=self.main_frame
        )
        self.input_radio_frame.pack(
            anchor="w"
        )

        self.input_radio = ctk.IntVar(value=1)
        self.spreadsheet_radio = ctk.CTkRadioButton(
            master=self.input_radio_frame,
            text="spreadsheet file",
            value=1,
            variable=self.input_radio,
            font=TEXT_FONT
        )

        self.spreadsheet_radio.pack(
            side="left",
            padx=(10,10)
        )

        self.sqlite_radio = ctk.CTkRadioButton(
            master=self.input_radio_frame,
            text="sqlite file",
            value=2,
            variable=self.input_radio,
            font=TEXT_FONT
        )
        self.sqlite_radio.pack(
            side="left"
        )

        self.file_selection_frame = ctk.CTkFrame(master=self.main_frame)
        self.file_selection_frame.pack(
            padx=(10,0),
            pady=(10,0),
            side="top",
            fill="both"
        )

        # display instruction to user: chose spreadsheet
        self.browse_file_label = ctk.CTkLabel(
            master=self.file_selection_frame,
            text="Select a file to process",
            font=TEXT_FONT
        )
        self.browse_file_label.pack(
            side="left",
            padx=(10,0),
            pady=(10,0)
        )
        
        # browse button open file dialog
        self.browse_file_btn = ctk.CTkButton(
            self.file_selection_frame,
            text="Browse",
            command=self.browse_file,
            font=TEXT_FONT
        )
        self.browse_file_btn.pack(
            padx=(10,0),
            pady=(10,0),
            side="left",
            anchor="nw"
        )

    def set_controller(self, controller):
        self.controller = controller

    def browse_file(self):
        """Open a file dialog window for spreadsheets files
        then display selected file
        """
        self.variables["input_radio"] = self.input_radio.get()
        if self.get_var("input_radio") == 1:

            self.filepath = ctk.filedialog.askopenfilename(
                title="Select a file",
                initialdir=os.path.expanduser("~"),
                filetypes=[("All Excel files", "*.xlsx *.xls *.xlsm *.xlsb *.odf *.ods *.odt")]
            )

            if self.filepath:
                # delete previous content if exist
                self.clean_stage(mode="all")
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
                self.clean_stage(mode="all")
                self.display_conversion_frame()
    
    def display_selected_file(self):

        self.selected_file = ctk.CTkLabel(
            master=self.main_frame,
            text=self.filepath,
            font=TEXT_FONT
        )
        self.selected_file.pack(
            anchor="w"
        )

        self.add_widget("selected_file", self.selected_file)

    def create_spreadsheet_frame(self):
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
            master=self.main_frame
        )
        self.spreadsheet_frame.pack(
            expand=True,
            fill="both",
        )
        self.add_frame("spreadsheet_frame", self.spreadsheet_frame)

        self.spreadsheet_frame_l = ctk.CTkFrame(
            master=self.spreadsheet_frame,
            height=400,
        )
        self.spreadsheet_frame_l.pack(
            expand=True,
            fill="x",
            side="left",
            padx=(10,10)
        )
        self.spreadsheet_frame_l.pack_propagate(False)
        self.add_frame("spreadsheet_frame_l", self.spreadsheet_frame_l)

        self.spreadsheet_frame_r = ctk.CTkFrame(
            master=self.spreadsheet_frame,
            height=400,
        )
        self.spreadsheet_frame_r.pack(
            expand=True,
            fill="x",
            side="right",
            padx=(10,10)
        )
        self.spreadsheet_frame_r.pack_propagate(False)
        self.add_frame("spreadsheet_frame_r", self.spreadsheet_frame_r)
    
    def display_spreadsheet_data(self):
        """Create treeviews to display data sheet"""

        # create treeview widget in spreadsheet_frame_l
        self.data_sheet_xscroll = ctk.CTkScrollbar(
            self.spreadsheet_frame_l,
            orientation="horizontal"
        )
        self.data_sheet = ttk.Treeview(
            master=self.spreadsheet_frame_l,
            xscrollcommand=self.data_sheet_xscroll.set
        )
        self.data_sheet.pack(
            side="top",
            expand=True,
            fill="both"
        )
        self.data_sheet_xscroll.pack(
            expand=True,
            fill="x"
        )
        self.data_sheet_xscroll.configure(command=self.data_sheet.xview)
        self.add_widget("data_sheet", self.data_sheet)

    def display_spreadsheet_meta(self):
        """Create treeviews to display metadata sheet"""

        # create treeview widget in spreadsheet_frame_r
        self.meta_sheet_xscroll = ctk.CTkScrollbar(
            self.spreadsheet_frame_r,
            orientation="horizontal"
        )       
        self.meta_sheet = ttk.Treeview(
            master=self.spreadsheet_frame_r,
            xscrollcommand=self.meta_sheet_xscroll.set
        )
        self.meta_sheet.pack(
            side="top",
            expand=True,
            fill="both"
        )
        self.meta_sheet_xscroll.pack(
            expand=True,
            fill="x"
        )
        self.meta_sheet_xscroll.configure(command=self.meta_sheet.xview)
        self.add_widget("meta_sheet", self.meta_sheet)

    def display_sheet_selector(self, tmp_data):
        """Add dropmenu for sheet selection to view"""

        table_list = [_ for _ in tmp_data.keys() if _ not in META_TABLES]
        table_list.insert(0, "Select a sheet")

        meta_table_list = [_ for _ in tmp_data.keys() if _ in META_TABLES]
        meta_table_list.insert(0, "Select a sheet")

        def sheet_selector_l_callback(choice, tmp_data):
            """Callback function that display sheet corresponding
            to user selection in drop menu
            """
            if self.get_widget("data_sheet") is not None:
                self.data_sheet.pack_forget()
                self.data_sheet_xscroll.pack_forget()
            if choice != "Select a sheet":
                self.display_data_sheet(tmp_data, choice)
        
        def sheet_selector_r_callback(choice, tmp_data):
            """Callback function that display sheet corresponding
            to user selection in drop menu
            """
            if self.get_widget("meta_sheet") is not None:
                self.meta_sheet.pack_forget()
                self.meta_sheet_xscroll.pack_forget()
            if choice != "Select a sheet":
                self.display_meta_sheet(tmp_data, choice)

        self.data_sheet_selector = ctk.CTkComboBox(
            master=self.spreadsheet_frame_l,
            values=table_list,
            command=lambda choice : sheet_selector_l_callback(choice, tmp_data),
            font=TEXT_FONT,
            # width=get_str_max_length(table_list)*8,
        )
        self.data_sheet_selector.pack(
            expand=True,
            fill="x",
            anchor="n"
        )
        self.add_widget("data_sheet_selector", self.data_sheet_selector)

        self.meta_sheet_selector = ctk.CTkComboBox(
            master=self.spreadsheet_frame_r,
            values=meta_table_list,
            command=lambda choice : sheet_selector_r_callback(choice, tmp_data),
            font=TEXT_FONT,
            # width=get_str_max_length(table_list)*8,
        )
        self.meta_sheet_selector.pack(
            expand=True,
            fill="x",
            anchor="n"
        )
        self.add_widget("meta_sheet_selector", self.meta_sheet_selector)
    
    def display_data_sheet(self, tmp_data, selected_sheet):
        """Called on sheet_selector's changes
        Update treeview widget to display selected data sheet
        """

        self.display_spreadsheet_data()

        self.data_sheet["column"] = list(tmp_data[selected_sheet].columns)
        self.data_sheet["show"] = "headings"
        for column in self.data_sheet["columns"]:
            self.data_sheet.heading(column, text=column)
        
        df_rows = tmp_data[selected_sheet].to_numpy().tolist()
        for row in df_rows:
            self.data_sheet.insert("", "end", values=row)
        
        self.data_sheet.bind("<Button-1>", lambda event: self.controller.on_header_click(event, selected_sheet))

    def display_meta_sheet(self, tmp_data, selected_sheet):
        """Called on sheet_selector's changes
        Update treeview widget to display selected metadata sheet
        """

        self.display_spreadsheet_meta()
        self.meta_sheet["column"] = list(tmp_data[selected_sheet].columns)
        self.meta_sheet["show"] = "headings"
        for column in self.meta_sheet["columns"]:
            self.meta_sheet.heading(column, text=column)
            if column in COLUMN_WIDTH_S:
                self.meta_sheet.column(column, width=50)
        
        df_rows = tmp_data[selected_sheet].to_numpy().tolist()

        for row in df_rows:
            self.meta_sheet.insert("", "end", values=row)
        
        self.meta_sheet.bind("<Button-1>", lambda event: self.controller.on_cell_click(event, selected_sheet))

    def display_upt_cell(self, value, x, y):
        """Display entry widget for changes in metadata table cell"""
        self.cell_entry = ctk.CTkEntry(self.data_sheet)
        self.cell_entry.insert(0, value)
        self.cell_entry.place(x=x,y=y)
        self.cell_entry.focus()
    
    #TODO update df, warning on non exist
    def display_spreadsheet_option(self):
        """Display buttons to create and update metadata tables
        and finally check spreadsheet
        """
        self.ss_option_frame = ctk.CTkFrame(
            master=self.main_frame
        )
        self.ss_option_frame.pack(
        )
        self.add_frame("ss_option_frame", self.ss_option_frame)

        self.display_save_spreadsheet()
        self.display_check_spreadsheet()


    #TODO: add control on metadata table content ?

    
    def display_check_spreadsheet(self):
        """Display check spreadsheet data button to check
        data consistency regarding template
        """
        self.check_btn = ctk.CTkButton(
            master=self.ss_option_frame,
            text="Check Spreadsheet data",
            font=TEXT_FONT,
            command=self.controller.verify_spreadsheet
        )
        self.check_btn.pack(
            side="left",
            anchor="center",
            padx=(10,10),
            pady=(10,10)
        )
        self.add_widget("check_btn", self.check_btn)
    
    def display_save_spreadsheet(self):
        """Display save changes button to save changes applied to the
        spreadsheet
        """
        self.save_btn = ctk.CTkButton(
            master=self.ss_option_frame,
            text="Save changes",
            font=TEXT_FONT,
            command=self.controller.save_changes
        )
        self.save_btn.pack(
            side="left",
            padx=(10,10),
            pady=(10,10)
        )
        self.add_widget("save_btn", self.save_btn)

    def display_errors(self, error_msg, error_type):
        """Display frame to show error find during spreadsheet check"""

        if self.get_frame("error_frame") is None:
            # create frame if not already exists
            self.error_frame = ctk.CTkFrame(master=self.main_frame)
            self.error_frame.pack(
                expand=True,
                fill="both"
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
            self.error_icon.pack(
                side="left"
            )

            self.errors = tk.Text(
                master=self.error_frame,
                background="#1d1e1e",
                foreground="white",
                border=0
            )

            self.errors.pack(
                side="left",
                padx=10,
                pady=5
            )

            self.errors_yscroll = ctk.CTkScrollbar(
                self.error_frame,
                orientation="vertical",
                command=self.errors.yview
            )
            self.errors_yscroll.pack(
                side="left",
                fill="y"
            )

            self.errors.configure(yscrollcommand=self.errors_yscroll.set)

            self.add_frame("error_frame", self.error_frame)

        if error_type == "data":
            self.errors.insert(tk.END, error_msg)
        elif error_type == "template":
            self.errors.insert(tk.END, error_msg)

    #TODO radio button only sqlite and erd OR all
    def display_conversion_frame(self):
        """Add a conversion frame to view with:
        - browse folder button for output directory selection
        - conversion option radio buttons
        (generate all, only sqlite and erd)
        """

        self.conversion_frame_label = ctk.CTkLabel(
            master=self.main_frame,
            text="Conversion options",
            font=SUBTITLE_FONT
        )
        self.conversion_frame_label.pack(
            padx=(10,0),
            pady=(20,0),
            anchor="w"
        )
        self.add_widget("conversion_frame_label", self.conversion_frame_label)

        self.conversion_frame = ctk.CTkFrame(master=self.main_frame)
        self.conversion_frame.pack(
            fill="both",
            expand=True,
            padx=(10,10),
            pady=(10,0)
        )
        self.add_frame("conversion_frame", self.conversion_frame)

        self.outdir_frame = ctk.CTkFrame(
            master=self.conversion_frame
        )
        self.outdir_frame.pack(
            fill="both",
            expand=True
        )

        self.outdir_label = ctk.CTkLabel(
            master=self.outdir_frame,
            text="Select a directory to store outputs",
            font=TEXT_FONT
        )
        self.outdir_label.pack(
            padx=10,
            pady=10,
            side="left"
        )

        self.outdir_btn = ctk.CTkButton(
            master=self.outdir_frame,
            command=self.browse_outdir,
            text="Browse Folder",
            font=TEXT_FONT
        )
        self.outdir_btn.pack(
            padx=10,
            pady=10,
            side="left"
        )

    def browse_outdir(self):
        """Open file dialog window to select output directory"""

        self.rm_filename_var()

        self.output_dir = ctk.filedialog.askdirectory(
            initialdir=os.path.expanduser("~")
        )

        if self.output_dir:
            if self.get_var("input_radio") == 2:
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

                self.filename_selection_frame=ctk.CTkFrame(
                    self.conversion_frame
                )
                self.filename_selection_frame.pack(
                    fill="both",
                    expand=True,
                )

                self.filename_entry(output_basename)
                self.ow_checkbox()

                self.convert_btn.pack(
                    padx=10,
                    pady=10
                )

        
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
            master=self.filename_selection_frame,
            textvariable=self.filename_var,
            font=TEXT_FONT,
            width=(get_str_max_length(self.filename_var.get()) + 15)*10
        )
        filename_entry.pack(
            side="left"
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
            master=self.filename_selection_frame,
            text="Overwrite existing file in output directory",
            variable=self.check_ow,
            command=lambda: callback_cb(self.filename_var.get()),
            onvalue="on",
            offvalue="off"
        )
        self.overwrite_cb.pack(
            side="left"
        )
    
    def open_edition_window(self, *args):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
            self.toplevel_window.edit_head_and_cell(*args)
        else:
            self.toplevel_window.focus()  # if window exists focus it
        
        return self.toplevel_window

    def display_convert_btn(self):
        """Display convert button to run sqlite, erd and pdf creation"""

        self.convert_btn = ctk.CTkButton(
            master=self.conversion_frame,
            text="Convert spreadsheet",
            command=self.controller.convert,
            state="disabled",
            font=TEXT_FONT
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
        self.file_exists_warning.pack(
        )

    def sqlite2pdf_btn(self):
        """Display a Generate PDF from sqlite button"""

        self.generate_btn = ctk.CTkButton(
            master=self.conversion_frame,
            text="Generate PDF",
            command=self.controller.sqlite2pdf,
        )
        self.generate_btn.pack(
            padx=10,
            pady=10
        )

    def show_success(self, msg):
        """ Open Window with success message"""
        CTkMessagebox(
            master=self.main_frame,
            title="Success",
            message=msg,
            icon="check",
            option_1="OK"
        )
    
    def warning_exit(self):
        """Open window to ask if user want to quit without saving"""
        msg_box = CTkMessagebox(
                    title="Pending Changes !",
                    message="Warning there are pending changes that haven't be saved yet!\nDo you want to save them ?",
                    option_1="Yes, save spreadsheet",
                    option_2="Quit without saving"
                )
        return msg_box

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
            del self.additional_frames[frame_name]
            frame.destroy()
    
    def rm_widget(self, widget_name):
        """Remove frame from view if exist"""

        if widget_name in self.additional_widgets:
            widget = self.get_widget(widget_name)
            del self.additional_widgets[widget_name]
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
    
    def erase_var_dict(self):
        """Delete every variable in self.variables dict"""
        self.variables = {}

    def clean_stage(self, mode="all"):
        """Remove frames and widgets from view, delete variables"""
        if mode=="all":
            self.rm_widget("selected_file")
            self.rm_frame("ss_option_frame")
            self.rm_frame("spreadsheet_frame")
            # self.rm_frame("spreadsheet_frame_l")
            # self.rm_frame("spreadsheet_frame_r")
            self.rm_widget("data_sheet_selector")
            self.rm_widget("meta_sheet_selector")
            self.rm_frame("error_frame")
            self.rm_widget("conversion_frame_label")
            self.rm_frame("conversion_frame")
            self.erase_var_dict()
        else:
            pass
    
    def rm_filename_var(self):
        """Remove previous filename variable if exist"""
        if "filename_var" in self.variables:
            del self.variables["filename_var"]
    