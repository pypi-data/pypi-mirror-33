"""
LED_Analyze - calc_basic
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from csv import reader
from os.path import split, splitext, exists
from tkinter import messagebox
import numpy as np
import re

from analysis_main import DataObject, ExtractVal, ExtractRange
from calc.calc_common import CalcProcess

class ExtractCSVVal(CalcProcess):
    """
    Extract a single value from the file referenced by path. Output
    a DataObject containing the value.
    """
    
    gui_commands = [
        ("FileInputFrame", "path", (400, "Delimited Text")),
        ("TextEntryFrame", "out_name", ("Name:", 200, 60)),
        ("SpboxFrame", "line",
         ("Line:", tuple(["Filename"] + list(range(1, 100))), 200, 60)),
        ("TextEntryFrame", "rule", ("Rule:", 200, 60)),
        ("CheckEntryFrame", "to_db", "Save to DB?")]
    
    def __init__(self, out_name, line, rule, path, to_db):
        
        self.name = "Extract Value"
        self.path = path
        self.line = line
        self.rule = rule
        self.out_name = out_name
        self.to_db = to_db
        CalcProcess.__init__(self, [])
        self.inputs = ["(From File)"]
        self.outputs.append(DataObject(out_name, None, self, self.to_db))
        
    def check(self):
        
        val = ExtractVal(
            self.name, self.line, self.rule, "---", "Delimited Text")
        
        if not val.check():
            return ("Value definition requires a valid name and rule/" +
                    "source. Rule/source must be a valid RegEx string " +
                    "for 'Delimited Text' file type or a valid cell " +
                    "reference for 'Spreadsheet' file type.")
        
        elif (self.path == "" or not exists(self.path)) \
                and type(self).__name__ != "ValFromTemplate":
            return "Value definition requires a valid file path."
        
        else:
            return None
    
    def run(self):
        
        # Handle extraction from data inside of the file
        if self.line != "Filename":
            
            # Open CSV and extract value
            with open(self.path, newline = "") as openfile:
                
                rd = reader(openfile)
                
                # Skip down to the desired line
                for i in range(0, self.line - 1):
                    next(rd)
                
                readline = next(rd)[0]
            
            # Cast output as a number if possible
            try:
                self.outputs[0].set(float(
                    re.search(self.rule, readline).group(1)))
            except ValueError:
                self.outputs[0].set(re.search(self.rule, readline).group(1))
        
        # Handle extraction from the filename
        else:
            
            filename = split(self.path)[1]
            filename = splitext(filename)[0]
            
            # Cast output as a number if possible
            try:
                self.outputs[0].set(
                    float(re.search(self.rule, filename).group(1)))
            except ValueError:
                self.outputs[0].set(
                    re.search(self.rule, filename).group(1))
                
        self.outputs[0].calc_hash = self.gen_hash()

class ExtractCSVRange(CalcProcess):
    """
    Extract a range from the file referenced by path. Output a DataObject
    containing the range.
    """
    
    gui_commands = [
        ("FileInputFrame", "path", (400, "Delimited Text")),
        ("TextEntryFrame", "out_name", ("Name:", 200, 60)),
        ("TextEntryFrame", "delim", ("Delimiter:", 100, 60)),
        ("TextEntryFrame", "rule", ("Rule:", 200, 60))]
    
    def __init__(self, out_name, delim, rule, path, to_db):
        
        self.name = "Extract Range"
        self.path = path
        self.delim = delim
        self.rule = []
        self.out_name = out_name
        self.to_db = to_db         
        CalcProcess.__init__(self, [])
        self.inputs = ["(From File)"]
        self.outputs.append(DataObject(
            out_name, np.array([None]), self, self.to_db))
        
        for item in rule.split(","):
            try:
                self.rule.append(int(item))
            except ValueError:
                self.rule.append(item)
                
    def check(self):
        
        rng = ExtractRange(self.name, self.rule, "---", "Delimited Text")
        
        if not rng.check():
            return ("Range definition requires a valid name and rule/source. " +
                    "Rule/source must be string of the form '#,#,#,#'.")
        
        elif self.delim == "":
            return "Range definition requires a valid delimiter character."
        
        elif (self.path == "" or not exists(self.path)) \
                and type(self).__name__ != "RngFromTemplate":
            return "Range definition requires a valid file path."
        
        else:
            return None
    
    def run(self):
        
        # Open CSV and extract range
        rng_out = []
        
        with open(self.path, newline = "") as openfile:
            
            rd = reader(openfile, delimiter = self.delim)
            count = self.rule[1] - 1
            
            # Skip any header rows
            for i in range(0, self.rule[1] - 1):
                next(rd)                
            
            # Create output array using self.rule to define range
            for row in rd:
                num_row = []
                row_test = False
                
                try:
                    row_test = count < self.rule[3]
                except:
                    pass
                
                if row_test or self.rule[3] == ":":
                    if self.rule[2] != ":":
                        for num in row[(self.rule[0] - 1):self.rule[2]]:
                            try:
                                num_row.append(float(num))
                            except ValueError:
                                if num != "\n":
                                    num_row.append(0)
                        rng_out.append(num_row)
                    
                    else:
                        for num in row[self.rule[0] - 1:]:
                            try:
                                num_row.append(float(num))
                            except ValueError:
                                if num != "":
                                    num_row.append(0)
                        rng_out.append(num_row)
                
                count += 1
            
            rng_out = np.array(rng_out)
            
        self.outputs[0].set(rng_out)
        self.outputs[0].calc_hash = self.gen_hash()
        
class ExtractSSValue(CalcProcess):
    """
    Extract a single value from the file referenced by path. Output
    a DataObject containing the value.
    """
    
    gui_commands = [
        ("FileInputFrame", "path", (400, "Spreadsheet")),
        ("TextEntryFrame", "out_name", ("Name:", 200, 60)),
        ("SpboxFrame", "sheet",
         ("Sheet:", list(range(0, 100)), 200, 60)),
        ("TextEntryFrame", "rule", ("Rule:", 200, 60))]
    
    def __init__(self, out_name, sheet, rule, path):
        
        self.name = "Extract Value"
        self.path = path
        self.sheet = sheet
        self.rule = rule
        self.out_name = out_name
        CalcProcess.__init__(self, [])
        self.inputs = ["(From File)"]
        self.outputs.append(DataObject(out_name, None, self))
        
    def check(self):
        
        val = ExtractVal(self.name, self.line, self.rule, "Delimited Text")
        
        if not val.check():
            return ("Value definition requires a valid name and rule/" +
                    "source. Rule/source must be a valid RegEx string " +
                    "for 'Delimited Text' file type or a valid cell " +
                    "reference for 'Spreadsheet' file type.")
        
        elif self.path == "" or not exists(self.path):
            return "Value definition requires a valid file path."
        
        else:
            return None
    
    def run(self):
        
        # Handle extraction from data inside of the file
        if self.line != "Filename":
            
            # Open CSV and extract value
            with open(self.path, newline = "") as openfile:
                
                rd = reader(openfile)
                
                # Skip down to the desired line
                for i in range(0, self.line - 1):
                    next(rd)
                
                readline = next(rd)[0]
            
            # Cast output as a number if possible
            try:
                self.outputs[0].set(float(
                    re.search(self.rule, readline).group(1)))
            except ValueError:
                self.outputs[0].set(re.search(self.rule, readline).group(1))
        
        # Handle extraction from the filename
        else:
            
            filename = split(self.path)[1]
            filename = splitext(filename)[0]
            
            # Cast output as a number if possible
            try:
                self.outputs[0].set(
                    float(re.search(self.rule, filename).group(1)))
            except ValueError:
                self.outputs[0].set(
                    re.search(self.rule, filename).group(1))
                
        self.outputs[0].calc_hash = self.gen_hash()

class ValFromTemplate(ExtractCSVVal):
    """
    Automatically generated process. Extract a value from an input data set
    based on the input template definition.
    """
    
    gui_commands = [
        ("CheckEntryFrame", "to_db", "Save to DB?")]
    
    def __init__(self, out_name, line, rule, suffix, to_db):
        ExtractCSVVal.__init__(self, out_name, line, rule, "", to_db)
        self.inputs = ["(From Template)"]
        self.suffix = suffix
        
class RngFromTemplate(ExtractCSVRange):
    """
    Automatically generated process. Extract a range from an input data set
    based on the input template definition.
    """
    
    gui_commands = [
        ("CheckEntryFrame", "to_db", "Save to DB?")]
    
    def __init__(self, out_name, delim, rule, suffix, to_db):
        ExtractCSVRange.__init__(self, out_name, delim, rule, "", to_db)
        self.inputs = ["(From Template)"]
        self.suffix = suffix