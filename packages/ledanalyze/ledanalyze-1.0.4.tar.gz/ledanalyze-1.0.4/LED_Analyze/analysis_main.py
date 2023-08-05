"""
LED_Analyze - analysis_main
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""

from os.path import split, splitext, exists
from copy import copy
import re
import numpy as np
import hashlib

class Analysis():
    """
    The main object that holds all data associated with a program
    session. The components are as follows:
    
    * templates - container holding all input format templates
    * inputs - container identifying all input data sets
    * calc - container defining all desired operations
    * outputs - container holding any generated output data
    """
    def __init__(self):
        
        self.templates = []
        self.inputs = []
        self.calcs = []
        self.outputs = []   
    
    def output_check(self, name, i):
        
        if i == None:
            for obj in self.outputs:
                if obj.name == name: return False
        else:
            for obj in self.outputs:
                if obj.name == name and obj not in self.calcs[i].outputs:
                    return False
        return True

class InputTemplate():
    """
    This object holds all data that defines the expected input data format.
    * file_type - Delimited Text or Spreadsheet
    * delim - Delimiter character
    * suffix - Filename suffix corr. to input template
    * vals - Definitions of Single Values to Extract
    * ranges - Definitions of Ranges to Extract
    """
    def __init__(self, name=None, file_type=None, delim=None, 
                 suffix="", vals=None, ranges=None):
        
        self.name = name
        self.file_type = file_type
        self.delim = delim
        self.suffix = suffix
        self.vals = vals if vals is not None else []
        self.ranges = ranges if ranges is not None else []
    
    def check_filename(self, path):
        
        # Test whether or not the given file path matches the pattern
        # expected given the template
        
        if self.file_type == "Delimited Text":
            
            if path[-4 - len(self.suffix):] in (
                self.suffix + ".txt", self.suffix + ".csv"):
                return(True, path[-4 - len(self.suffix):])
            
            else:
                return(False, None)
        
        elif self.file_type == "Spreadsheet":
            if path[-4 - len(self.suffix):] == self.suffix + ".xls":
                return(True, path[-4 - len(self.suffix):])
            
            elif path[-5 - len(self.suffix):] in (
                self.suffix + ".xlsx",
                self.suffix + ".xlsm"):
                return(True, path[-5 - len(self.suffix):])
            
            else:
                return(False, None)
    
    def check(self):
        
        # Test whether the given inputs are valid
        
        if self.name == "":
            return False
        elif self.delim == "" and self.file_type == "Delimited Text":
            return False
        elif len(self.vals) + len(self.ranges) == 0:
            return False
        return True

class ExtractVal():
    """
    A definition for a single value extraction
    """
    def __init__(self, name, line, rule, sheet, file_type):
        self.name = name
        self.line = line
        self.rule = rule
        self.sheet = sheet
        self.file_type = file_type
        
        if file_type == "Delimited Text":
            self.sheet = "---"
    
    def check(self):
        
        if "" in (self.name, self.rule):
            return False
        if self.file_type == "Delimited Text":
            try: 
                re.compile(self.rule)
            except re.error:
                return False
        elif self.file_type == "Spreadsheet":
            if not re.match("([\$]?[A-Z]+[\$]?[0-9]+)", self.rule):
                return False
        else:
            return False
                    
        return True

class ExtractRange():
    """
    A definition for a range extraction
    """
    def __init__(self, name, rule, sheet, file_type):
        self.name = name
        self.rule = rule
        self.sheet = sheet
        self.file_type = file_type
        
        if file_type == "Delimited Text":
            self.sheet = "---"
    
    def check(self):
        
        if "" in (self.name, self.rule):
            return False
        
        if self.file_type == "Delimited Text":
            if isinstance(self.rule, str):
                parse_rule = self.rule.split(",")
            else:
                parse_rule = self.rule
            
            if len(parse_rule) != 4:
                return False
            
            for i in range(0, 4):
                try:
                    parse_rule[i] = int(parse_rule[i])
                except ValueError:
                    if i not in (2, 3):
                        return False
                    elif parse_rule[i] != ":":
                        return False
        
        elif self.file_type == "Spreadsheet":
            if not re.match(
                "([\$]?[A-Z]+[\$]?[0-9]+[:][\$]?[A-Z]+[\$]?[0-9]+)"):
                return False
        
        else:
            return False
        
        return True            

class DataSet():
    """
    A single set of data adhering to the currently committed data template.
    * name - Common filename
    * path - Directory to data set files
    * tails - List of filename tails including suffix and extension
    """
    def __init__(self, name, path, tails):
        self.name = name
        self.path = path
        self.tails = tails
        self.input_hash = []
        
    @classmethod
    def from_templates(cls, templates, path):
        
        # Alternate constructor. Takes a list of input templates and a 
        # path to a file. 
        # Conditions:
        # * the path matches an input template.  
        # * files matching the other templates are present in the same 
        #   directory.
        # Returns None if conditions are not met
        
        temp_match = cls.check_path(templates, path)

        tails = [None] * len(templates)
        
        if temp_match == None:
            return None
        else:
            remainder = templates.copy()
            remainder.remove(temp_match[0])
            
            tails[templates.index(temp_match[0])] = temp_match[1]
            
            folder, name = split(path)
            folder = folder.replace("/", "\\")
            name = splitext(name)[0][:-len(temp_match[0].suffix)]
            
            for temp in remainder:
                for ext in (".txt", ".csv"):
                    check_name = folder + "\\" + name + temp.suffix + ext
                    
                    if all((
                        exists(check_name),
                        temp.file_type == "Delimited Text")):
                        tails[templates.index(temp)] = temp.suffix + ext
                
                for ext in (".xls", ".xlsx", ".xlsm"):
                    check_name = folder + "\\" + name + temp.suffix + ext
                    
                    if all((
                        exists(check_name),
                        temp.file_type == "Spreadsheet")):
                        tails[templates.index(temp)] = temp.suffix + ext
            
            if len(remainder) + 1 != len(tails):
                return None
            
            else:
                return DataSet(name, folder, tails)
                        
    @staticmethod
    def check_path(templates, path):
        
        # Checks if a given path matches any of the given templates
        # Returns the template and filename tail if so; None if not.
    
        for temp in templates:
            out = temp.check_filename(path)
            if out[0]:
                return (temp, out[1])
        
        return None
    
    def gen_hash(self):
        
        # Generate hash for each file referenced by the DataSet object
        # and store in the self.input_hash list.
        
        self.input_hash = []
        
        hasher = hashlib.sha1()
        block_size = 65536
        
        for tail in self.tails:
            with open(self.path + "\\" + self.name + tail, 'rb') as hashfile:
                buf = hashfile.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = hashfile.read(block_size)
            
            self.input_hash.append(hasher.hexdigest())

class DataObject:
    """
    An object holding a set of data, including a name, and a hash of and
    a reference to the object that generated it.
    """
    def __init__(self, name, data, calc, to_db=False):
        
        self.name = name
        self.__data = data
        self.to_db = to_db
        self.calc = calc
        self.calc_hash = 0
        
        if np.shape(self.__data) == ():
            self.__type = "Scalar"
        else:
            self.__type = "Array"
        
    @property
    def read_data(self):
        return copy(self._DataObject__data)
    
    @property
    def type(self):
        return self._DataObject__type
    
    def set(self, value):
        
        self._DataObject__data = value
        
        if np.shape(value) == ():
            self._DataObject__type = "Scalar"
        else:
            self._DataObject__type = "Array"
        