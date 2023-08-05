"""
LED_Analyze - gui_input_template
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from tkinter import *
from tkinter import messagebox
from copy import deepcopy

from gui_common import *
from analysis_main import InputTemplate, ExtractVal, ExtractRange

class TemplateScrFrame(SelectableScrFrame):
    """
    Scrolling frame to be placed within InputTemplateFrame. Display 
    template data currently contained within data_ref container where 
    data_ref is the list of uncommitted input templates.
    """
    def __init__(self, master, data_ref):
        
        header = (("", 35),
                  ("Input Name",90),
                  ("File Type", 75),
                  ("Delimiter", 75),
                  ("Suffix", 75),
                  ("Outputs", 100))
        
        SelectableScrFrame.__init__(self, master, data_ref, header, 125)
    
    def update_data(self, start=0):
        
        # Update data contained in the data_lines container with the current
        # data in the data_ref container
        
        new_data_lines = []
        
        # Extract data from each template to generate label text
        for template in self.data_ref[start:]:
            new_line = []
            new_line.append(template.name)
            new_line.append(template.file_type)
            new_line.append(template.delim)
            new_line.append(template.suffix)
            
            # Extract just the names of the values/ranges
            ext_names = []
            
            for ext_single in template.vals:
                ext_names.append(ext_single.name)
                ext_names.append("\n")
            for ext_range in template.ranges:
                ext_names.append(ext_range.name)
                ext_names.append("\n")
            name_str = "".join(ext_names)[:-1]
            new_line.append(name_str)
            
            new_data_lines.append(new_line)
        
        del self.data_lines[start:]
        self.data_lines.extend(new_data_lines)
    
    def add_line(self):
        gui = AddTemplateGUI(self.data_ref, self, None)
        gui.lift(self.master)
        
    def edit_line(self, i):
        if len(self.data_ref) != 0:
            gui = AddTemplateGUI(self.data_ref, self, i)
            gui.lift(self.master)
    
    def remove_line(self, i):
        if len(self.data_ref) != 0:
            del self.data_ref[i]
            self.update_data(i)
            self.reconcile_lines(i)
    
class SingleScrFrame(SelectableScrFrame):
    """
    Scrolling frame to be placed within an instance of InputTemplateGUI. 
    Display info for single value extractions currently contained 
    within data_ref container where data_ref is uncommitted data for a 
    single input template.
    """
    def __init__(self, master, data_ref, file_type):
        
        header = (("", 35),
                  ("Value Name",100),
                  ("Line", 60),
                  ("Sheet", 40),
                  ("Rule/Source", 180))
        
        SelectableScrFrame.__init__(self, master, data_ref, header, 150)
        self.file_type = file_type
        
    def update_data(self):
        
        # Update data contained in the data_lines container with the current
        # data in the templates_uncomm container
        
        self.data_lines = []
        
        for val in self.data_ref.vals:
            new_line = []
            new_line.append(val.name)
            new_line.append(val.line)
            new_line.append(val.sheet)
            new_line.append(val.rule)
            self.data_lines.append(new_line)
        
    def add_line(self):
        gui = AddSingleValueGUI(self.data_ref, self, self.file_type, None)
        gui.lift(self.master)
    
    def edit_line(self, i):
        if len(self.data_ref.vals) != 0:
            AddSingleValueGUI(self.data_ref, self, self.file_type, i)
        
    def remove_line(self, i):
        if len(self.data_ref.vals) != 0: 
            del self.data_ref.vals[i]
            self.update_data()
            self.reconcile_lines(i) 

class RangeScrFrame(SelectableScrFrame):
    """
    Scrolling frame to be placed within an instance of InputTemplateGUI. 
    Display info for range extractions currently contained within data_ref 
    container where data_ref is uncommitted data for a single input 
    template.
    """
    def __init__(self, master, data_ref, file_type):
        header = (("", 35),
                  ("Range Name", 150),
                  ("Sheet", 50),
                  ("Rule/Source", 180))
        
        SelectableScrFrame.__init__(self, master, data_ref, header, 150)
        self.file_type = file_type
    
    def update_data(self):
        
        # Update data contained in the data_lines container with the current
        # data in the templates_uncomm container
            
        self.data_lines = []
        
        for rng in self.data_ref.ranges:
            new_line = []
            new_line.append(rng.name)
            new_line.append(rng.sheet)
            new_line.append(rng.rule)
            self.data_lines.append(new_line)
    
    def add_line(self):
        AddRangeGUI(self.data_ref, self, self.file_type, None)
    
    def edit_line(self, i):
        if len(self.data_ref.ranges) != 0:
            AddRangeGUI(self.data_ref, self, self.file_type, i)
        
    def remove_line(self, i):
        if len(self.data_ref.ranges) != 0:
            del self.data_ref.ranges[i]
            self.update_data()
            self.reconcile_lines(i)

class InputTemplateFrame(LabelFrame):
    """
    Frame to be placed on the main GUI screen containing the 
    SelectableScrFrame displaying current input templates
    """
    def __init__(self, master, data_ref, commit_flag):
        
        LabelFrame.__init__(self, master)
        
        # Initialize attributes
        self.data_ref = data_ref # Ref to current committed templates
        self.data_uncomm = deepcopy(data_ref)
        self.commit_flag = commit_flag
        
        # Configure frame
        self.config(text = "Input Template")
        self.columnconfigure(0, minsize=5)
        for i in range(1, 5):
            self.columnconfigure(i, minsize=100)
        self.columnconfigure(5, minsize=5)
        
        # Create TemplateScrFrame
        self.scrframe = TemplateScrFrame(self, self.data_uncomm)
        self.scrframe.grid(
            row=1, column=1, columnspan=4, pady=2)
        
        # Create buttons
        button_data = (
            ("Add Template", self.scrframe.add_line, 0, 1),
            ("Edit", 
             lambda: self.scrframe.edit_line(self.scrframe.sel_line.get()), 
             0, 3),
            ("Remove", 
             lambda: self.scrframe.remove_line(self.scrframe.sel_line.get()), 
             0, 4),
            ("Commit", self.commit, 2, 3),
            ("Un-Commit", self.ask_uncommit, 2, 4)
        )
        
        self.buttons = []
        
        for i, (name, call, r, c) in enumerate(button_data):
            
            self.buttons.append(
                Button(self,
                       text=name,
                       width=15,
                       command=call)
                )
            
            self.buttons[i].grid(row=r, column=c, pady=5)
        
        self.buttons[4].config(state=DISABLED)
    
    def ask_uncommit(self):
        
        result = messagebox.askokcancel(
            "Confirm Un-Commit",
            "Are you sure you want to un-commit the input " +
            "template data? Doing so will clear out all " +
            "other analysis data.",
            parent=self)
        
        if result:
            self.uncommit()
    
    def commit(self):
        
        data_comm = deepcopy(self.data_uncomm)
        self.data_ref.clear()
        self.data_ref.extend(data_comm)
        self.commit_flag.set(True)
        
    def uncommit(self):
        
        self.data_uncomm.clear()
        
        for template in self.data_ref:
            copy_temp = deepcopy(template)
            self.data_uncomm.append(copy_temp)
            
        self.commit_flag.set(False)
    
    def soft_commit(self):
        
        data_comm = deepcopy(self.data_uncomm)
        self.data_ref.clear()
        self.data_ref.extend(data_comm)
        
class TemplateExtractFrame(LabelFrame):
    
    def __init__(self, master, data_ref, label, file_type):
        
        LabelFrame.__init__(self, master)
        self.config(text=label)
        
        # Initialize attributes
        self.master = master
        self.data_ref = data_ref # Ref to the uncommitted template data
        
        # Create Frame
        if label == "Extract Single Value":
            self.scrframe = SingleScrFrame(self, self.data_ref, file_type)
        
        elif label == "Extract Range":
            self.scrframe = RangeScrFrame(self, self.data_ref, file_type)
        
        self.scrframe.grid(
            row=2, column=1, columnspan=4)
        
        self.rowconfigure(0, minsize=2)
        self.columnconfigure(0, minsize=5)
        for i in range(1, 5):
            self.columnconfigure(i, minsize=100)
        self.columnconfigure(5, minsize=5)
        self.rowconfigure(3, minsize=5)
        
        # Create buttons
        button_data = (
            ("Add", self.scrframe.add_line, 1, 1),
            ("Edit", 
             lambda: self.scrframe.edit_line(self.scrframe.sel_line.get()), 
             1, 3),
            ("Remove", 
             lambda: self.scrframe.remove_line(self.scrframe.sel_line.get()), 
             1, 4)
        )
        
        self.buttons = []
        
        for i, (name, call, r, c) in enumerate(button_data):
            
            self.buttons.append(
                Button(self,
                       text=name,
                       width=13,
                       command=call)
                )
            self.buttons[i].grid(row=r, column=c, pady=5)

class AddTemplateGUI(Toplevel):
    """
    GUI pop up window that allows the user to define an input file template
    including:
    
    * Template name
    * Template file type (delimited text or excel)
    * Template filename suffix
    * Output data to be extracted (name and rule)
    """
    def __init__(self, data_ref, display, i=None):
        
        # Create and configure base window
        Toplevel.__init__(self)
        self.title("Define Input Data Template - CSV Analyzer")
        self.resizable(False, False)
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(3, minsize=5)
        
        # Initialize attributes
        self.data_ref = data_ref # Ref to the list of uncommitted templates
        self.display = display # Ref to the display frame that called this GUI
        self.i = i
        
        if self.i == None:
            self.data_uncomm = InputTemplate() # Empty template
            self.data_uncomm.file_type = "Delimited Text"
            self.data_uncomm.delim = ","
        
        else:
            self.data_uncomm = deepcopy(self.data_ref[i])
        
        # Insert input frames
        self.name_in = TextEntryFrame(
            self,
            "Template Name:",
            225, 95)
        self.name_in.grid(row=1, column=1, sticky=W)
        
        self.type_in = ComboboxFrame(
            self,
            "File Type:",
            ("Delimited Text", "Spreadsheet"),
            225, 95)
        self.type_in.grid(row=2, column=1, sticky=W)
        
        self.delim_in = TextEntryFrame(
            self,
            "Delimiter:",
            150, 65)
        self.delim_in.grid(row=2, column=2, sticky=W)
        
        self.suff_in = TextEntryFrame(
            self,
            "Filename Suffix:",
            225, 95)
        self.suff_in.grid(row=3, column=1, sticky=W)
        
        # Create "Single Value Extract" and "Range Extract" frames
        self.single_frame = TemplateExtractFrame(
            self, 
            self.data_uncomm, 
            "Extract Single Value", 
            self.data_uncomm.file_type)
        self.single_frame.grid(
            row=4, column=1, columnspan=2, pady=2, sticky=W)
        
        self.range_frame = TemplateExtractFrame(
            self, 
            self.data_uncomm, 
            "Extract Range", 
            self.data_uncomm.file_type)
        self.range_frame.grid(
            row=5, column=1, columnspan=2, pady=2, sticky=W)
        
        # Create Buttons
        btn_ok = Button(
            self, text="OK", width=15,
            command=self.commit)
        btn_ok.grid(row=6, column=2, pady=5, sticky=E)
        
        # Prefill data if necessary 
        if i != None:
            self.name_in.entry_input.set(data_ref[i].name)
            self.type_in.combox_input.set(data_ref[i].file_type)
            self.delim_in.entry_input.set(data_ref[i].delim)
            self.suff_in.entry_input.set(data_ref[i].suffix)
            
            self.single_frame.scrframe.update_data()
            self.single_frame.scrframe.reconcile_lines()
            self.range_frame.scrframe.update_data()
            self.range_frame.scrframe.reconcile_lines()
        
        # Wipe data if window closes
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Clear extraction values and ranges and enable/disable delimiter
        # entry box on file type change
        self.type_in.combox_input.trace("w", self.type_change)
    
    def commit(self):
        
        # Move template data in self.data_uncomm to the data container 
        # referenced by self.data_ref
        
        self.data_uncomm.name = self.name_in.entry_input.get()
        self.data_uncomm.file_type = self.type_in.combox_input.get()
        self.data_uncomm.delim = self.delim_in.entry_input.get()
        self.data_uncomm.suffix = self.suff_in.entry_input.get()
        
        # Show error message if required fields are empty
        if not self.data_uncomm.check():            
            messagebox.showerror(
                "User Input Error",
                "Invalid input given for template definition." +
                "Template definition must have a name, valid delimiter " +
                "character, and at least one extraction value or range.",
                parent=self)
        
        elif self.i == None:
            self.data_ref.append(self.data_uncomm)
            self.display.update_data(len(self.data_ref) - 1)
            self.display.reconcile_lines(len(self.data_ref) - 1)
            self.destroy()
        
        else:
            del self.data_ref[self.i]
            self.data_ref.insert(self.i, self.data_uncomm)
            self.display.update_data(self.i)
            self.display.reconcile_lines(self.i)
            self.destroy()

    def on_close(self):
        
        self.destroy()
        self.data_uncomm.vals.clear()
        self.data_uncomm.ranges.clear()
        
    def type_change(self, *args):
        
        self.data_uncomm.vals.clear()
        self.data_uncomm.ranges.clear()
        self.single_frame.scrframe.update_data()
        self.single_frame.scrframe.reconcile_lines()
        self.range_frame.scrframe.update_data()
        self.range_frame.scrframe.reconcile_lines()
        self.data_uncomm.file_type = self.type_in.combox_input.get()
        self.single_frame.scrframe.file_type = self.type_in.combox_input.get()
        self.range_frame.scrframe.file_type = self.type_in.combox_input.get()
        
        if self.type_in.combox_input.get() == "Delimited Text":
            self.delim_in.enable()
        else:
            self.delim_in.disable()
        
class AddSingleValueGUI(Toplevel):
    """
    GUI pop up window that allows the user to specify the value to be
    extracted.
    """
    def __init__(self, data_ref, display, file_type, i=None):
        
        # Initialize and configure window
        Toplevel.__init__(self)
        self.title("Extract Single Value")
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(2, minsize=5)
        
        # Intialize attributes
        self.data_ref = data_ref # Ref to the uncommitted template
        self.display = display # Ref to the display frame that called this GUI
        self.i = i
        self.store = ExtractVal("", "Filename", "", "", file_type)
        self.file_type = file_type
        
        # Create data entry frames
        self.name_in = TextEntryFrame(
            self,
            "Name:",
            250, 75)
        self.name_in.grid(row=1, column=1, sticky=W)
        
        if file_type == "Delimited Text":
            line_vals = tuple(["Filename"] + list(range(1, 100)))
        else:
            line_vals = ("---")
        self.line_in = SpboxFrame(
            self,
            "Line:",
            line_vals,
            200, 75)
        self.line_in.grid(row=2, column=1, sticky=W)
        
        if file_type == "Spreadsheet":
            sheet_vals = tuple(["Filename"] + list(range(0, 100)))
        else:
            sheet_vals = ("---")
        self.sheet_in = SpboxFrame(
            self,
            "Sheet:",
            sheet_vals,
            200, 75)
        self.sheet_in.grid(row=3, column=1, sticky=W)
        
        self.rule_in = TextEntryFrame(
            self,
            "Rule/Source:",
            250, 75)
        self.rule_in.grid(row=4, column=1, sticky=W)
        
        if i != None:
            self.name_in.entry_input.set(data_ref.vals[i].name)
            self.line_in.spbox_input.set(data_ref.vals[i].line)
            self.sheet_in.spbox_input.set(data_ref.vals[i].sheet)
            self.rule_in.entry_input.set(data_ref.vals[i].rule)
        
        # Create Add button
        btn_add = Button(
            self,
            text="Accept",
            command=self.commit)
        btn_add.grid(row=5, column=1, pady=5, sticky=E)
    
    def commit(self):
        
        # Check if name exists in extract values/ranges for current
        # set of uncommitted templates
        check_name = True
        
        for template in self.display.master.master.data_ref:
            for obj in (template.vals + template.ranges): 
                if self.name_in.entry_input.get() == obj.name:
                    check_name=False
        
        # Give error for duplicate name
        if not check_name:
            messagebox.showerror(
                "User Input Error",
                "Name given to value is already in use. Please use " +
                "a different name.")
        
        # Perform check for empty input and add data to template 
        else:
            self.store.name = self.name_in.entry_input.get()
            self.store.rule = self.rule_in.entry_input.get()
            
            if self.file_type == "Delimited Text":
                if self.line_in.spbox_input.get() == "Filename":
                    self.store.line = self.line_in.spbox_input.get()
                else:
                    self.store.line = int(self.line_in.spbox_input.get())
                self.store.sheet = self.sheet_in.spbox_input.get()
            
            if self.file_type == "Spreadsheet":
                if self.sheet_in.spbox_input.get() == "Filename":
                    self.store.sheet = self.sheet_in.spbox_input.get()
                else:
                    self.store.sheet = int(self.sheet_in.spbox_input.get())
                
            # Show error if there are empty fields
            if not self.store.check():
                messagebox.showerror(
                    "User Input Error",
                    "Value definition requires a valid name and rule/source. " +
                    "Rule/source must be a valid RegEx string for 'Delimited " +
                    "Text' file type or a valid cell reference for " +
                    "'Spreadsheet' file type.",
                    parent=self)
                
            elif self.i == None:
                self.data_ref.vals.append(self.store)
                self.display.update_data()
                self.display.reconcile_lines(len(self.data_ref.vals) - 1)
                self.destroy()
            
            else:
                del self.data_ref.vals[self.i]
                self.data_ref.vals.insert(self.i, self.store)
                self.display.update_data()
                self.display.reconcile_lines(self.i)
                self.destroy()

class AddRangeGUI(Toplevel):
    """
    GUI pop up window that allows the user to specify the range to be
    extracted.
    """
    def __init__(self, data_ref, display, file_type, i=None):
        
        # Initialize and configure window
        Toplevel.__init__(self)
        self.title("Extract Range")
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(2, minsize=5)
        
        # Initialize attributes
        self.data_ref = data_ref # Ref to the uncommitted template
        self.display = display # Ref to the display frame that called this GUI
        self.i = i
        self.store = ExtractRange("", "", "", file_type)
        
        # Create data entry frames
        self.name_in = TextEntryFrame(
            self,
            "Name:",
            250, 75)
        self.name_in.grid(row=1, column=1, sticky=W)
        
        if file_type == "Spreadsheet":
            sheet_vals = tuple(range(0, 100))
        else:
            sheet_vals = ("---")
        self.sheet_in = SpboxFrame(
            self,
            "Sheet:",
            sheet_vals,
            200, 75)
        self.sheet_in.grid(row=2, column=1, sticky=W)
        
        self.rule_in = TextEntryFrame(
            self,
            "Rule/Source:",
            250, 75)
        self.rule_in.grid(row=3, column=1, sticky=W)
        
        # Prefill data if necessary
        if i != None:
            self.name_in.entry_input.set(data_ref.ranges[i].name)
            self.sheet_in.spbox_input.set(data_ref.ranges[i].sheet)
            self.rule_in.entry_input.set(data_ref.ranges[i].rule)
        
        # Create Add button
        btn_add = Button(
            self,
            text="Accept",
            command=self.commit)
        btn_add.grid(row=4, column=1, pady=5, sticky=E)
        
    def commit(self):
        
        # Check if name exists in extract values/ranges for current
        # set of uncommitted templates
        check_name = True
        
        for template in self.display.master.master.data_ref:
            for obj in (template.vals + template.ranges): 
                if self.name_in.entry_input.get() == obj.name:
                    check_name = False
        
        # Give error for duplicate name
        if not check_name:
            messagebox.showerror(
                "User Input Error",
                "Name given to value is already in use. Please use " +
                "a different name.",
                parent=self)
        
        # Perform check for empty input and add data to template 
        else:
            self.store.name = self.name_in.entry_input.get()
            self.store.rule = self.rule_in.entry_input.get()
            
            if self.sheet_in.spbox_input.get() == "---":
                self.store.sheet = self.sheet_in.spbox_input.get()
            else:
                self.store.sheet = int(self.sheet_in.spbox_input.get())
                    
            # Show error if there are empty fields
            if not self.store.check():
                messagebox.showerror(
                    "User Input Error",
                    "Range definition requires a valid name and rule/source. " +
                    "Rule/source must be string of the form '#,#,#,#' for "+
                    "'Delimited Text' file type or a valid range reference for " +
                    "'Spreadsheet' file type.",
                    parent=self)
            
            elif self.i == None:
                self.data_ref.ranges.append(self.store)
                self.display.update_data()
                self.display.reconcile_lines(len(self.data_ref.ranges) - 1)
                self.destroy()
            
            else:
                del self.data_ref.ranges[self.i]
                self.data_ref.ranges.insert(self.i, self.store)
                self.display.update_data()
                self.display.reconcile_lines(self.i)
                self.destroy()