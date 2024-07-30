# controller.py
import os
import customtkinter as ctk
from src.gui.view import View
from src.gui.model import Model
from src.extraction.check import InvalidData

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def load_spreadsheet(self, spreadsheet_path):
        self.model.spreadsheet_path = spreadsheet_path
        tmp_data = self.model.load_spreadsheet(spreadsheet_path)
        self.view.display_data(tmp_data)

    def verify_spreadsheet(self):
        """Control spreadsheet is conform
        if not display errors
        else display browse directory for output and convert button
        """
        try:
            self.model.verify_spreadsheet()
        except InvalidData as e:
            self.view.display_errors(str(e).replace("str: ", ""))
        else:
            self.view.allow_conversion()
    
    # def convert_all(self,  output_dir):

    #     self.model.output_path = output_dir
    #     self.model.