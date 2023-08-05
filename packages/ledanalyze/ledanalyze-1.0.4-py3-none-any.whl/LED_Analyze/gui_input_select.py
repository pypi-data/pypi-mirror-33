"""
LED_Analyze - gui_input_select
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from tkinter import filedialog
from tkinter import *
from os import listdir
from os.path import isfile, join

from gui_common import SelectableScrFrame
from analysis_main import DataSet, InputTemplate

class InputScrFrame(SelectableScrFrame):
    """
    Scrolling frame to be placed within the InputSelectFrame on the
    main GUI screen. Displays currently selected data sets that will
    be used in the analysis. 
    """
    def __init__(self, master, data_ref, templates):
        
        header = (("", 35),
                  ("Data Set Name", 165),
                  ("Directory", 250))
        
        SelectableScrFrame.__init__(self, master, data_ref, header, 125)
        self.templates = templates # Ref to the list of committed templates
    
    def update_data(self):
        
        self.data_lines.clear()
        for data_set in self.data_ref:
            self.data_lines.append([data_set.name, data_set.path])
    
    def get_single(self):
        
        # Choose a single input data set from one file selection
        
        path = filedialog.askopenfilename(
            initialdir = "C:\\",
            title = "Select an input data file",
            filetypes = (("Delimited Text Files", "*.txt"),
                         ("Delimited Text Files", "*.csv"),
                         ("Excel Files", "*.xls"),
                         ("Excel Files", "*.xlsx"),
                         ("Excel Files", "*.xlsm"))
            )
        self.add_line(path)
        
    def get_folder(self):
        
        # Select a folder to scour all files fitting the current set
        # of input templates
        
        folder = filedialog.askdirectory(
            initialdir = "C:\\",
            title = "Select a folder to search for inputs")
        
        file_types = (".txt", ".csv", ".xls", ".xlsx", ".xlsm")
        
        files = [
            file for file in listdir(folder) if all((
                isfile(join(folder, file)),
                file.endswith(file_types)))
            ]
        
        for file in files:
            self.add_line(join(folder, file))
    
    def add_line(self, path):
        
        new_set = DataSet.from_templates(self.templates, path)
        
        if new_set != None:
            new_set.gen_hash()
            
            if [new_set.name, new_set.path] not in self.data_lines:
                self.data_ref.append(new_set)
                self.update_data()
                self.reconcile_lines()
        
    def remove_line(self, i):
        
        if len(self.data_ref) != 0:
            del self.data_ref[i]
            self.update_data()
            self.reconcile_lines(i)
        
class InputSelectFrame(LabelFrame):
    """
    Frame to be placed on the main GUI screen containing the
    SelectableScrFrame displaying current input data sets
    """
    def __init__(self, master, data_ref, templates):
        
        LabelFrame.__init__(self, master)
        
        # Initialize attributes
        self.data_ref = data_ref # Ref to current list of data sets
        
        # Configure frame
        self.config(text = "Input Data")
        self.columnconfigure(0, minsize = 5)
        for i in range(1, 5):
            self.columnconfigure(i, minsize = 100)
        self.columnconfigure(5, minsize = 5)
        
        # Create TemplateScrFrame
        self.scrframe = InputScrFrame(self, data_ref, templates)
        self.scrframe.grid(
            row = 1, column = 1, columnspan = 4, pady = 2)
        
        # Create buttons
        button_data = (
            ("Add Single", self.scrframe.get_single, 0, 1),
            ("Add Folder", self.scrframe.get_folder, 0, 2),
            ("Remove", lambda: self.scrframe.remove_line(
                self.scrframe.sel_line.get()), 0, 4)
            )
        
        self.buttons = []
        
        for i, (name, call, r, c) in enumerate(button_data):
            
            self.buttons.append(
                Button(self,
                       text = name,
                       width = 15,
                       command = call,
                       state = DISABLED)
                )
            
            self.buttons[i].grid(row = r, column = c, pady = 5)
        
        