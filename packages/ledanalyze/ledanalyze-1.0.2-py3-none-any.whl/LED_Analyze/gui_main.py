"""
LED_Analyze - gui_main
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""

from tkinter import *
from tkinter import messagebox, filedialog
import numpy as np
import pickle
from os.path import splitext, split, exists

from analysis_main import *
from gui_input_template import *
from gui_input_select import *
from gui_calc import *
from gui_output import *

class MainGUI(Tk):
    
    def __init__(self, data_ref):
        
        Tk.__init__(self)
        self.title("LED Analyzer")
        
        self.data_ref = data_ref
        self.commit_flag = BooleanVar(value=False)
        self.input_keys = [] # Names of valid database input keys (rows)
        self.scalar_vals = [] # Names of valid database scalar values (columns)
        self.array_vals = [] # Names of valid database array values (columns)
        
        # Database File Input
        self.db_file_frame = DatabaseSelectFrame(
            self)
        self.db_file_frame.grid(row=0, column=0, columnspan=2,
                                padx=5, pady=5)
        
        self.db_path = self.db_file_frame.path
        
        # Input Template Display
        self.temp_frame = InputTemplateFrame(
            self, 
            self.data_ref.templates,
            self.commit_flag)
        self.temp_frame.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Input Data Set Selection Display
        self.input_frame = InputSelectFrame(
            self, 
            self.data_ref.inputs,
            self.data_ref.templates)
        self.input_frame.grid(
            row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Calculation Setup Display
        self.calc_frame = CalcFrame(
            self,
            self.data_ref)
        self.calc_frame.grid(
            row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Input Dataset Key Selection Frame
        self.input_key_frame = InputKeyFrame(self)
        self.input_key_frame.grid(
            row=0, column=2, padx=5, pady=5, sticky=N+S)
        
        # Report Template Frame
        self.report_temp_frame = ReportTemplateFrame(self)
        self.report_temp_frame.grid(
            row=1, column=2, rowspan=3, padx=5, pady=5, sticky=N+S+W+E)
        
        # Output Buttons
        self.output_frame = OutputDataFrame(self)
        self.output_frame.grid(
            row=4, column=2, pady=5)
        
        # Save and Load Analysis Settings
        Button(
            self, 
            text="Save Analysis Settings",
            command=self.save, 
            width=25,
            height=1).grid(
                row=4, column=0, pady=5)
            
        Button(
            self,
            text="Load Analysis Settings",
            command=self.load,
            width=25,
            height=1).grid(
                row=4, column=1, pady=5)
        
        self.commit_flag.trace("w", self.gui_commit)
    
    def gui_commit(self, *args):
        
        # Clear all input selections, calculations, and saved outputs
        # if the template settings are un-committed. Enable input
        # selection, calculation, and output viewing if committed.
        
        if self.commit_flag.get():
            
            for i in range(0, 4):
                self.temp_frame.buttons[i].config(state=DISABLED)
            self.temp_frame.buttons[4].config(state="normal")
            
            for button in self.input_frame.buttons:
                button.config(state="normal")
            for button in self.calc_frame.buttons:
                button.config(state="normal")
            
            self.calc_frame.scrframe.extract_from_templates()
                
        else:
            for i in range(0, 4):
                self.temp_frame.buttons[i].config(state="normal")
            self.temp_frame.buttons[4].config(state=DISABLED)
            
            for button in self.input_frame.buttons:
                button.config(state=DISABLED)
            for button in self.calc_frame.buttons:
                button.config(state=DISABLED)
            
            self.data_ref.calcs.clear()
            self.calc_frame.scrframe.update_data()
            self.calc_frame.scrframe.reconcile_lines()
            self.data_ref.outputs.clear()
                
    def save(self):
        
        # Save analysis settings (templates, calculation steps)
        # to a file to enable retrieval and reuse
        
        path = filedialog.asksaveasfilename(
            initialdir="C:\\",
            title="Save analysis settings to file",
            defaultextension=".csvset",
            filetypes=[("Analysis Settings", ".csvset")])
        
        savefile = open(path, 'wb')
        pkl = pickle.Pickler(savefile)
        pkl.dump(self.data_ref)
        
    def load(self):
        
        # Load analysis settings from external file
        
        path = filedialog.askopenfilename(
            initialdir="C:\\",
            title="Load analysis settings from file",
            defaultextension=".csvnet",
            filetypes=[("Analysis Settings", ".csvset")])
        
        loadfile = open(path, 'rb')
        unpkl = pickle.Unpickler(loadfile)
        new_data = unpkl.load()
        
        # Clear out templates
        self.temp_frame.uncommit()
        self.temp_frame.data_uncomm.clear()
        self.temp_frame.commit()
        
        # Add in pickled templates
        self.temp_frame.data_uncomm.extend(new_data.templates)
        self.temp_frame.scrframe.update_data()
        self.temp_frame.scrframe.reconcile_lines()
        self.temp_frame.soft_commit()
        
        # Add in pickled calcs and outputs
        self.data_ref.calcs.extend(new_data.calcs)
        self.data_ref.outputs.extend(
            [obj for calc in self.data_ref.calcs for obj in calc.outputs])
        self.calc_frame.scrframe.update_data()
        self.calc_frame.scrframe.reconcile_lines()
                
class DatabaseSelectFrame(LabelFrame):
    """
    Frame to be placed within the main GUI that allows the user
    to select the database file to which all data will be saved.
    """
    def __init__(self, master):
        
        LabelFrame.__init__(self, master)
        
        # Initialize attributes
        self.path = StringVar()
        
        # Configure Frame
        self.config(text="Database File Input")
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, minsize=310)
        self.columnconfigure(2, minsize=80)
        self.columnconfigure(3, minsize=80)
        self.columnconfigure(4, minsize=5)
        self.rowconfigure(2, minsize=5)
        
        self.display = Entry(
            self,
            state="readonly",
            textvariable=self.path)
        self.display.grid(
            row=1, column=1, padx=5, sticky=W+E)
        
        Button(
            self,
            text="New",
            command=self.create_db,
            width=9).grid(row=1, column=2, sticky=E)
        
        Button(
            self,
            text="Open",
            command=self.get_db,
            width=9).grid(row=1, column=3, sticky=E)
            
    def create_db(self):
        
        path = filedialog.asksaveasfilename(
            title="Create new output database",
            initialdir="C:\\",
            filetypes=[("Database Files", "*.bd")])
        
        path, _ = splitext(path)
        dir, _ = split(path)
        
        if exists(dir):
            path = path + ".bd"        
            self.path.set(path)
        
        # Set valid keys as the list of possible data sets for output
        # report generation and close database
        self.master.input_keys = []
        self.master.scalar_vals = []
        self.master.array_vals = []
        self.master.input_key_frame.update()
        self.master.report_temp_frame.update()
        self.master.input_key_frame.clear()
        self.master.report_temp_frame.clear()
    
    def get_db(self):
        
        path = filedialog.askopenfilename(
            title="Open output database",
            initialdir="C:\\",
            filetypes=[("Database Files", "*.bd")])
        self.path.set(path)
        
        # Open database and get list of datasets with non-NULL data entries
        analysis_db = AnalysisDatabase(path)
        keys = analysis_db.get_keys()
        headers = [header for header in analysis_db.get_data_headers() \
                   if header != "id"]
        valid_keys = []
         
        for key in keys:
            vals = [analysis_db.get_val(key, header) for header in headers]
            if not all([isinstance(val, type(None)) for val in vals]):
                valid_keys.append(key)
         
        # Get list of database columns with non-NULL data entries
        valid_headers = []
         
        for header in headers:
            vals = [analysis_db.get_val(key, header) for key in keys]
            if not all([isinstance(val, type(None)) for val in vals]):
                valid_headers.append(header)
         
        # Separate into valid list of scalar type and array type columns
        valid_scalar_headers = [header for header in valid_headers \
                                if analysis_db.get_col_type(header) == "Scalar"]
         
        valid_array_headers = [header for header in valid_headers \
                               if analysis_db.get_col_type(header) == "Array"]
         
        # Set valid keys as the list of possible data sets for output
        # report generation and close database
        self.master.input_keys = valid_keys
        self.master.scalar_vals = valid_scalar_headers
        self.master.array_vals = valid_array_headers
        self.master.input_key_frame.update()
        self.master.report_temp_frame.update()
        
#         self.master.input_key_frame.clear()
        self.master.report_temp_frame.clear()
        
        analysis_db.close()