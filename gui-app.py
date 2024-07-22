import customtkinter as ctk
import tkinter as tk

from conf import conf

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

        # display instruction to user
        self.browse_label = ctk.CTkLabel(
            master=self.input_frame,
            text="Select a spreadsheet to convert into sqlite database"
        )
        self.browse_label.grid(
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
            command=self.browse_file(filetypes=[("All Excel files", "*.xlsx;*.xls;*.xlsm;*.xlsb;*.odf;*.ods;*.odt")])
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
            "pady":(10, 0)
        }
        self.selected_file.grid_forget()

        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=1)

    # open file dialog
    def browse_file(self, filetypes):
        """Open a file dialog window, then display selected file"""
        filepath = ctk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=filetypes
        )
        if filepath:
            self.update_labels(
                self.selected_file,
                f"Selected file: {filepath}",
                grid_option=self.selected_file_grid_options
            )
        
     
    def update_labels(self, label, value, grid_option=None):
        """Update the selected label text attribute with value
        """
        label.configure(text=value)
        if grid_option is not None:
            label.grid(**grid_option)



if __name__ == "__main__":
    app = App()
    # app.attributes("-fullscreen", "True")
    app.mainloop()