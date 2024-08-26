import os
import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

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
                # TODO ?? rm children from dict store and separate dict frame from dict widget
                self.rm_widget("error_frame")
                self.rm_widget("conversion_frame")
                self.controller.spreadsheet_loader(self.filepath)
        
        else:
            self.filepath = ctk.filedialog.askopenfilename(
                title="Select a file",
                filetypes=[("sqlite File", "*.sqlite")]
            )
            
            if self.filepath:
                self.rm_widget("error_frame")
                self.rm_widget("conversion_frame")
                self.controller.display_conversion_frame()
            

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

    def convert_spreadsheet_option(self):
        # TODO: add checkbox to enable full process or only sqlite + erd
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

    def delete_elmt(self, widget_name):
        """Delete widget/frame and childrens"""

        to_del_obj = self.additional_widgets.get(widget_name)
        to_del_obj.delete(*to_del_obj.get_children())

    def get_var(self, var_name):
        """Return variable value from dict
        if key doesn't exist, return None
        """
        return self.variables.get(var_name, None)
