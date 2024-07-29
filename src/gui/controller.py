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

    def verify_spreadsheet(self, spreadsheet_path):
        self.model.spreadsheet_path = spreadsheet_path

        try:
            self.model.verify_spreadsheet()
        except InvalidData as e:
            self.view.display_errors(str(e).replace("str: ", ""))
        else:
            self.view.sheets_dict = self.model.data.sheets_dict
            self.view.display_data()