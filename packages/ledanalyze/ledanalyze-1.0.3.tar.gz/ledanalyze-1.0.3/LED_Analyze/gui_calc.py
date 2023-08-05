"""
LED_Analyze - gui_calc
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from tkinter import *
from db import *
from tkinter import font, messagebox
from tkinter.ttk import Combobox
from gui_common import *
from calc.calc_basic import *
from calc.calc_led import *

from math import ceil
from copy import copy, deepcopy
from collections import Iterable
from multiprocessing import Pool, cpu_count

# Lists that are used in operation selection comboboxes in the
# Add Calc Step GUI menu
_calc_names_basic = ["Extract Value - Delimited Text",
                     "Extract Range - Delimited Text",
                     "Extract Value From Template",
                     "Extract Range From Template"]

_calc_cls_basic = ["ExtractCSVVal",
                   "ExtractCSVRange",
                   "ValFromTemplate",
                   "RngFromTemplate"]

_calc_names_color = ["Center and Crop",
                     "Generate Mask",
                     "Uniformity",
                     "Heatmap Statistics",
                     "Light Leakage",
                     "Chromaticity Statistics",
                     "Dominant Wavelength"]

_calc_cls_color = ["CropCtr",
                   "GenMask",
                   "Uniformity",
                   "HeatmapStats",
                   "LightLeakage",
                   "ChromStats",
                   "DominantWL"]

_calc_types = {"Basic": (_calc_names_basic, _calc_cls_basic),
               "Colorimetry": (_calc_names_color, _calc_cls_color)}

class CalcScrFrame(SelectableScrFrame):
    """
    Scrolling frame to be placed within the CalcFrame on the main GUI
    window. Displays currently selected data processing steps.
    """
    def __init__(self, master, data_ref):

        header = (
            ("", 35),
            ("Inputs", 120),
            ("Calculation Step", 175),
            ("Outputs", 120))
        
        SelectableScrFrame.__init__(self, master, data_ref, header, 125)
        self.templates = data_ref.templates
    
    def add_line(self):
        CalcStepGUI(self.data_ref, self)
    
    def edit_line(self, i):
        CalcStepGUI(self.data_ref, self, i)
    
    def remove_line(self, i):
        
        # Disallow removal of template derived data
        if isinstance(
                self.data_ref.calcs[i], 
                (ValFromTemplate, RngFromTemplate)):
            messagebox.showerror(
                "Action Not Allowed",
                "Data derived from template definitions may not be " + \
                  "deleted. Edit template definition to remove.",
                parent=self)
        else:
            if len(self.data_ref.calcs[i].children) != 0:
                ok_to_delete = messagebox.askokcancel(
                    "Dependency Warning",
                    "You are about to delete a calculation step whose " + \
                      "outputs are used in subsequent steps. Continuing " + \
                      "will delete all dependent calculation steps as well.",
                    parent=self)
                
                if ok_to_delete:
                    garbage_list = self.data_ref.calcs[i].remove_data()
                    
                    # Delete all affected calcs
                    for obj in garbage_list[0]:
                        self.data_ref.calcs.remove(obj)
                    
                    # Delete all affected outputs
                    for obj in garbage_list[1]:
                        self.data_ref.outputs.remove(obj)
                    
                    self.update_data()
                    self.reconcile_lines()
            
            else:
                for obj in self.data_ref.calcs[i].outputs:
                    self.data_ref.outputs.remove(obj)
                
                del self.data_ref.calcs[i]
                self.update_data()
                self.reconcile_lines()
            
    def update_data(self):
        
        # Update the ScrFrame data display with the current data
        # contained in the data_ref container
        new_data_lines = []
        
        for step in self.data_ref.calcs:
            new_line = []
            
            # Get names of inputs
            in_names = []
            for obj in step.inputs:
                if isinstance(obj, str):
                    in_names.append(obj)
                else:
                    in_names.append(obj.name)
                in_names.append("\n")
            name_str = "".join(in_names)[:-1]
            new_line.append(name_str)
            
            new_line.append(step.name)
            
            # Get names of outputs
            out_names = []
            for obj in step.outputs:
                if obj.to_db:
                    add_name = obj.name + "*"
                else:
                    add_name = obj.name
                out_names.append(add_name)
                out_names.append("\n")
            name_str = "".join(out_names)[:-1]
            new_line.append(name_str)
                
            new_data_lines.append(new_line)
        
        self.data_lines = new_data_lines
    
    def extract_from_templates(self):
        
        # For every desired output defined by the input data templates,
        # create a calculation step to extract the data
        for template in self.templates:
            if template.file_type == "Delimited Text":
                
                for val in template.vals:
                    new_val_step = ValFromTemplate(
                        val.name, val.line, val.rule, template.suffix, False)
                    self.data_ref.calcs.append(new_val_step)
                    self.data_ref.outputs.extend(new_val_step.outputs)
                
                for rng in template.ranges:
                    new_rng_step = RngFromTemplate(
                        rng.name, template.delim, rng.rule, 
                        template.suffix, False)
                    self.data_ref.calcs.append(new_rng_step)
                    self.data_ref.outputs.extend(new_rng_step.outputs)
            
            else:
                pass # Supposed to handle for Spreadsheets. Ignore
                    
        self.update_data()
        self.reconcile_lines()
        
class CalcFrame(LabelFrame):
    """
    Frame to be placed on the main GUI window showing the calculation
    display frame
    """
    def __init__(self, master, data_ref):
        
        LabelFrame.__init__(self, master)
        self.data_ref = data_ref
        
        # Configure frame
        self.config(text="Calculation Setup")
        self.columnconfigure(0, minsize=5)
        for i in range(1, 5):
            self.columnconfigure(i, minsize=100)
        self.columnconfigure(5, minsize=5)
        
        # Create display frame
        self.scrframe = CalcScrFrame(self, data_ref)
        self.scrframe.grid(row=1, column=1, columnspan=4, pady=2)
        
        # Create buttons
        button_data = (
            ("Add Step", self.scrframe.add_line, 0, 1),
            ("Edit", 
             lambda: self.scrframe.edit_line(self.scrframe.sel_line.get()), 
             0, 3),
            ("Remove", 
             lambda: self.scrframe.remove_line(self.scrframe.sel_line.get()), 
             0, 4)
        )
        
        self.buttons = []
        
        for i, (name, call, r, c) in enumerate(button_data):
            
            self.buttons.append(
                Button(self,
                       text=name,
                       width=15,
                       command=call,
                       state=DISABLED)
                )
            
            self.buttons[i].grid(row=r, column=c, pady=5)
        
        big_font = font.Font(family="Segoe UI", size = 14, weight = "bold")
        self.buttons.append(
            Button(self,
                   text="RUN CALCULATIONS",
                   bg="purple3",
                   fg="white",
                   command=self.run_all,
                   font=big_font,
                   width=40,
                   height=2,
                   bd=4))
        
        self.buttons[-1].grid(
            row=2, column=1, columnspan=4, pady=5)
    
    def run_all(self):
        
        if len(self.data_ref.inputs) == 0:
            messagebox.showerror(
                "No Input Data",
                "Select at least one input data set to continue running " \
                  + "calculations.",
                parent = self.master)            
            return None
        
        analysis_db = AnalysisDatabase(
            self.master.db_file_frame.path.get())
        
        # Check if outputs that need to be saved to the database
        # match the database data_table column headers
        outputs_to_db = [[obj.name for obj in self.data_ref.outputs \
                          if obj.to_db],
                         [obj for obj in self.data_ref.outputs \
                          if obj.to_db]]
        analysis_db.reconcile_data_headers(outputs_to_db)
        
        # Check if list of input datasets matches the database
        # data_table row keys
        data_rows = [obj.path + "\\" + obj.name \
                     for obj in self.data_ref.inputs]
        analysis_db.reconcile_data_rows(data_rows)
    
        # Make copy sets of data to send out to individual processes
        proc_data = []
        
        for dataset in self.data_ref.inputs:
            proc_data.append(
                deepcopy(self.data_ref))
            proc_data[-1].templates = []
            proc_data[-1].inputs = [copy(dataset)]
        
        num_cores = cpu_count()
        
        # Break job up into sets that may be simultaneously carried
        # out and then stuffed into the database when complete
        for i in range(ceil(len(proc_data) / num_cores)):
            
            # Break off each batch
            proc_batch = proc_data[:num_cores]
            proc_data = proc_data[num_cores:]
            
            # Create and run pool
            calc_pool = Pool(processes=num_cores)
            output_batch = calc_pool.map(run_calc, proc_batch)
            
            # Unload batch data to the database
            for name, outputs in output_batch:
                for output in outputs:
                    if output.to_db:
                        analysis_db.insert_val(
                            name, output.name, output.read_data)
            
            output_batch = []
        
        # Get list of datasets with non-NULL data entries
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
        
        analysis_db.close()

class CalcStepGUI(Toplevel):
    """
    GUI that allows the user to specify and define a calculation step.
    """
    def __init__(self, data_ref, display, i=None):
        
        # Initialize and configure window
        Toplevel.__init__(self)
        self.title("Define Calculation Step")
        self.rowconfigure(1, minsize=5)
        self.rowconfigure(3, minsize=5)
        
        # Initialize attributes
        self.data_ref = data_ref # Ref to the analysis data container
        self.display = display # Ref to GUI display showing calc steps
        self.data_select = []
        self.param_frame = None
        self.calc = None
        self.i = i
        
        # Generate valid list of value selections for ComboBoxes
        if i == None:
            self.vals = [
                obj for obj in self.data_ref.outputs \
                if obj.type == "Scalar"]
            self.val_names = [obj.name for obj in self.vals]
            
            self.ranges = [
                obj for obj in self.data_ref.outputs \
                if obj.type == "Array"]
            self.rng_names = [obj.name for obj in self.ranges]
        
        else:
            self.vals = [
                obj for obj in self.data_ref.outputs \
                if obj.type == "Scalar" and \
                not obj.calc.test_inheritance(self.data_ref.calcs[i]) and \
                obj not in self.data_ref.calcs[i].outputs]
            self.val_names = [obj.name for obj in self.vals]
            
            self.ranges = [
                obj for obj in self.data_ref.outputs \
                if obj.type == "Array" and \
                not obj.calc.test_inheritance(self.data_ref.calcs[i]) and \
                obj not in self.data_ref.calcs[i].outputs]
            self.rng_names = [obj.name for obj in self.ranges]
        
        # Create operation selection drop down menu
        self.category_select = ComboboxFrame(
            self,
            "Operation Type:",
            list(_calc_types.keys()),
            350, 100)
        self.category_select.grid(row=0, column=0, sticky=W)
        self.category_select.combox_input.set("Basic")
        
        self.op_select = ComboboxFrame(
            self,
            "Operation Select:",
            _calc_types[self.category_select.combox_input.get()][0],
            350, 100)
        self.op_select.grid(row=1, column=0, sticky=W)
        
        if i != None:
            
            for obj in _calc_types.keys():
                
                op_cls = type(self.data_ref.calcs[i]).__name__
                
                if op_cls in _calc_types[obj][1]:
                    self.category_select.combox_input.set(obj)
                    self.update_op_select()
                    self.op_select.combox_input.set(
                        _calc_types[obj][0][_calc_types[obj][1].index(op_cls)])
                    self.update_op_params()
                    break
                
            self.prefill()
        
        # Watch for updates to comboboxes
        self.category_select.combox_input.trace("w", self.update_op_select)
        self.op_select.combox_input.trace("w", self.update_op_params)
        
    def update_op_select(self, *args):
        
        self.op_select.combox.configure(
            values = _calc_types[self.category_select.combox_input.get()][0])
        
    def update_op_params(self, *args):
        
        chosen_op = self.op_select.combox_input.get()
        
        # Prevent user from creating an extract from template operation
        if self.i == None and chosen_op in \
                ("Extract Value From Template", "Extract Range From Template"):
            
            if self.param_frame != None:
                self.param_frame.destroy()
                
            messagebox.showerror(
                "Action Not Allowed",
                "This type of operation is automatically generated from " \
                  + "an input template and may not be manually created.",
                parent=self)
            
        else:
            op_list = _calc_types[self.category_select.combox_input.get()]
            
            if self.param_frame != None:
                self.param_frame.destroy()
            
            exec("self.calc = " + op_list[1][op_list[0].index(chosen_op)])
            self.gen_calc_gui()
        
    def gen_calc_gui(self):
        
        # Automatically generate a calculation option GUI based on
        # the data contained in each calc object's gui_commands list
        # of definitions. Each list gets parsed, generating a string
        # that is executed as an exec() statement.
        
        # Create and configure frame
        self.param_frame = LabelFrame(self)
        self.param_frame.config(text = "Calculation Parameters")
        self.param_frame.columnconfigure(0, minsize=5)
        self.param_frame.columnconfigure(2, minsize=5)
        self.param_frame.rowconfigure(
            len(self.calc.gui_commands)+2, minsize=5)
        
        self.check_in = []
        self.file_in = []
        self.text_in = []
        self.spbox = []
        self.combox = []
        self.select_name = []
        
        self.param_frame.grid(row=2, column=0, padx=5, pady=5)
        
        # Create widgets based on gui_command definitions in calc
        for j, obj in enumerate(self.calc.gui_commands):
            
            if obj[0] == "CheckEntryFrame":
                self.check_in.append(
                    CheckEntryFrame(
                        self.param_frame, obj[2]))
                self.check_in[-1].grid(
                    row=j+1, column=1, sticky=W, padx=5, pady=5)
            
            elif obj[0] == "FileInputFrame":
                self.file_in.append(
                    FileInputFrame(
                        self.param_frame,
                        obj[2][0], obj[2][1]))
                
                self.file_in[-1].grid(
                    row=j+1, column=1, sticky=W)
                
            elif obj[0] == "TextEntryFrame":
                self.text_in.append(
                    TextEntryFrame(
                        self.param_frame,
                        obj[2][0], obj[2][1], obj[2][2]))
                self.text_in[-1].grid(
                    row=j+1, column=1, sticky=W)
                
            elif obj[0] == "SpboxFrame":
                self.spbox.append(
                    SpboxFrame(
                        self.param_frame,
                         obj[2][0], obj[2][1], obj[2][2], obj[2][3]))
                self.spbox[-1].grid(
                    row=j+1, column=1, sticky=W)
                
            elif obj[0] == "ComboboxFrame":
                if isinstance(obj[3], bool):
                    select_list = self.rng_names if obj[3] else self.val_names
                else:
                    select_list = obj[3]
                
                self.combox.append(
                    ComboboxFrame(
                        self.param_frame,
                        obj[2][0], select_list, obj[2][1], obj[2][2]))
                self.combox[-1].grid(
                    row=j+1, column=1, sticky=W)
                
            elif obj[0] == "SelectNameLabelFrame":
                
                if not isinstance(obj[2][0], str):
                    vals = [self.rng_names if obj[3] else self.val_names] * \
                      len(obj[2][0])
                else:
                    vals = self.rng_names if obj[3] else self.val_names
                
                self.select_name.append(
                    SelectNameLabelFrame(
                        self.param_frame,
                        vals,
                        obj[2][0], obj[2][1], obj[2][2], 
                        obj[2][3], obj[2][4]))
                
                self.select_name[-1].grid(
                    row=j+1, column=1, sticky=W)
                
            else:
                return None
            
        Button(
            self.param_frame,
            text="Confirm",
            width=20,
            command=self.commit).grid(
                row=len(self.calc.gui_commands)+1, column=1, pady=5, sticky=E)
            
    def prefill(self):
        
        # Automatically prefills data from an existing calc into an
        # automatically generated calc step GUI. Used when the user
        # tries to edit an existing calc step.
        
        self.category_select.combox.configure(state="disabled")
        self.op_select.combox.configure(state="disabled")
        
        counts = {
            "CheckEntryFrame": 0,
            "FileInputFrame": 0,
            "TextEntryFrame": 0,
            "SpboxFrame": 0,
            "ComboboxFrame": 0,
            "SelectNameLabelFrame": 0}
        
        # Loop through all gui elements and prefill data from existing
        # calc instance located in analysis data container
        for obj in type(self.data_ref.calcs[self.i]).gui_commands:
            
            if obj[0] == "CheckEntryFrame":
                exec("self.check_in[" + str(counts[obj[0]]) + "].flag.set(" + \
                  "self.data_ref.calcs[self.i]." + obj[1] + ")")
            
            if obj[0] == "FileInputFrame":
                exec("self.file_in[" + str(counts[obj[0]]) + "].path.set(" + \
                       "self.data_ref.calcs[self.i]." + obj[1] + ")")
            
            elif obj[0] == "TextEntryFrame":
                exec("self.text_in[" + str(counts[obj[0]]) + \
                       "].entry_input.set(self.data_ref.calcs[self.i]." + \
                     str(obj[1]) + ")")
            
            elif obj[0] == "SpboxFrame":
                exec("self.spbox[" + str(counts[obj[0]]) + \
                       "].spbox_input.set(self.data_ref.calcs[self.i]." + \
                     str(obj[1]) + ")")
            
            elif obj[0] == "ComboboxFrame":
                
                # If definition implies the combobox selects 
                # existing DataObjects
                if isinstance(obj[3], bool):
                    
                    # Select name from existing array type DataObjects
                    if obj[3]:
                        exec("self.combox[" + str(counts[obj[0]]) + \
                               "].combox_input.set(self.rng_names[" +\
                               "self.ranges.index(self.data_ref.calcs[" + \
                               "self.i]." + str(obj[1]) + ")])")
                    
                    # Select name from existing scalar type DataObjects
                    else:
                        exec("self.combox[" + str(counts[obj[0]]) + \
                               "].combox_input.set(self.val_names[" +\
                               "self.vals.index(self.data_ref.calcs[" + \
                               "self.i]." + str(obj[1]) + ")])")
                
                else:               
                    exec("self.combox[" + str(counts[obj[0]]) + \
                           "].combox_input.set(self.data_ref.calcs[" + \
                           "self.i]." + str(obj[1]) + ")")
            
            elif obj[0] == "SelectNameLabelFrame":
                
                # Fill in multiple selection comboxes
                if not isinstance(obj[1][0], str):
                    
                    # Selection consists of existing array type outputs
                    if obj[3]:
                        for i, _ in enumerate(obj[1][0]):
                            exec("self.select_name[" + str(counts[obj[0]]) + \
                                   "].combox_input[" + str(i) + "].set(" + \
                                   "self.rng_names[self.ranges.index(" + \
                                   "self.data_ref.calcs[self.i]." + 
                                   str(obj[1][0][i]) + ")])")
                    
                    # Selection consists of existing scalar type outputs
                    else:
                        for i, _ in enumerate(obj[1][0]):
                            exec("self.select_name[" + str(counts[obj[0]]) + \
                                   "].combox_input[" + str(i) + "].set(" + \
                                   "self.val_names[self.vals.index(" + \
                                   "self.data_ref.calcs[self.i]." + \
                                   str(obj[1][0][i]) + ")])")
                        
                # Fill in single selection combox
                else:
                    if obj[3]:
                        exec("self.select_name[" + str(counts[obj[0]]) + \
                               "].combox_input.set(" + \
                               "self.rng_names[self.ranges.index(" + \
                               "self.data_ref.calcs[self.i]." + 
                               str(obj[1][0]) + ")])")
                    
                    # Selection consists of existing scalar type outputs
                    else:
                        exec("self.select_name[" + str(counts[obj[0]]) + \
                               "].combox_input.set(" + \
                               "self.val_names[self.vals.index(" + \
                               "self.data_ref.calcs[self.i]." + \
                               str(obj[1][0]) + ")])")
                
                # Fill in multiple output entry
                if not isinstance(obj[1][1], str):
                    for i, _ in enumerate(obj[1][1]):
                        exec("self.select_name[" + str(counts[obj[0]]) + \
                               "].entry_input[" + str(i) + \
                               "].set(self.data_ref.calcs[self.i]." + \
                               str(obj[1][1][i]) + ")")
                        exec("self.select_name[" + str(counts[obj[0]]) + \
                               "].db_flag[" + str(i) + \
                               "].set(self.data_ref.calcs[self.i]." + \
                               str(obj[1][2][i]) + ")")
                
                # Fill in single output entry
                else:        
                    exec("self.select_name[" + str(counts[obj[0]]) + \
                           "].entry_input.set(self.data_ref.calcs[self.i]." + \
                           str(obj[1][1]) + ")")
                    exec("self.select_name[" + str(counts[obj[0]]) + \
                           "].db_flag.set(self.data_ref.calcs[self.i]." + \
                           str(obj[1][2]) + ")")
            
            counts[obj[0]] += 1
        
    def commit(self):
        
        # Take entries made by the user into the automatically generated
        # calc step GUI and use them to generate instances of the desired
        # calc objects. Each entry gets read based on the calc object's
        # gui_commands list. The read data gets added to a string that is
        # executed using an exec() statement.
        
        ldict = locals()
        
        counts = {
            "CheckEntryFrame": 0,
            "FileInputFrame": 0,
            "TextEntryFrame": 0,
            "SpboxFrame": 0,
            "ComboboxFrame": 0,
            "SelectNameLabelFrame": 0}
        
        # Check that all comboboxes have an input selected
        for obj in (self.combox + self.select_name):
            try:
                test = [obj.combox_input.get()]
            except AttributeError:
                test = [item.get() for item in obj.combox_input]
                
            if any([item == "" for item in test]):
                messagebox.showerror(
                    "User Input Error",
                    "Please select an item in all drop down selections.",
                    parent=self)
                return None
        
        op_select = self.op_select.combox_input.get()
        
        # Generate exec command string to create the desired calc instance
        if op_select == "Extract Value From Template":
            exec_line = "data_uncomm = " + str(self.calc.__name__) + "(" \
              + "out_name=\'" + self.data_ref.calcs[self.i].outputs[0].name \
              + "\', line=\'" + str(self.data_ref.calcs[self.i].line) + "\', " \
              + "rule=\'" + self.data_ref.calcs[self.i].rule + "\', suffix=\'" \
              + self.data_ref.calcs[self.i].suffix + "\', "
        
        elif op_select == "Extract Range From Template":
            rng_rule = str(self.data_ref.calcs[self.i].rule)
            rng_rule = rng_rule.replace("[", "").replace("]", "")
            rng_rule = rng_rule.replace(" ","").replace("\'", "")
            
            exec_line = "data_uncomm = " + str(self.calc.__name__) + "(" \
              + "out_name=\'" + self.data_ref.calcs[self.i].outputs[0].name \
              + "\', delim=\'" + self.data_ref.calcs[self.i].delim + "\', " \
              + "rule=\'" + rng_rule + "\', suffix=\'" \
              + self.data_ref.calcs[self.i].suffix + "\', "
        
        else:
            exec_line = "data_uncomm = " + str(self.calc.__name__) + "("
        
        for obj in self.calc.gui_commands:
            
            if obj[0] == "CheckEntryFrame":
                exec_line += obj[1] + "=self.check_in[" + \
                  str(counts[obj[0]]) + "].flag.get(), "
            
            if obj[0] == "FileInputFrame":
                exec_line += obj[1] + "=self.file_in[" + \
                  str(counts[obj[0]]) + "].path.get(), "
            
            elif obj[0] == "TextEntryFrame":
                exec_line += obj[1] + "=self.text_in[" + \
                  str(counts[obj[0]]) + "].entry_input.get(), "
            
            elif obj[0] == "SpboxFrame":
                exec_line += obj[1] + "=self.spbox[" + str(counts[obj[0]]) + \
                  "].spbox_input.get(), "
            
            elif obj[0] == "ComboboxFrame":
                
                # If definition implies the combobox selects 
                # existing DataObjects
                if isinstance(obj[3], bool):
                    
                    # Select from existing array type DataObjects
                    if obj[3]:
                        exec_line += obj[1] + "=self.ranges[" + \
                          "self.rng_names.index(self.combox[" + \
                          str(counts[obj[0]]) + "].combox_input.get())], "
                    
                    # Select from existing scalar type DataObjects
                    else:
                        exec_line += obj[1] + "=self.vals[" + \
                          "self.val_names.index(self.combox[" + \
                          str(counts[obj[0]]) + "].combox_input.get())], "
                
                else:
                    exec_line += obj[1] + "=self.combox[" + \
                      str(counts[obj[0]]) + "].combox_input.get(), "
            
            elif obj[0] == "SelectNameLabelFrame":
                
                # Define inputs to calculation
                if not isinstance(obj[1][0], str):
                    for i, item in enumerate(obj[1][0]):
                        exec_line += item
                        
                        # Choose correct array type DataObject based on selected 
                        # name
                        if obj[3]:
                            exec_line += "=self.ranges[self.rng_names." + \
                              "index(self.select_name[" + \
                              str(counts[obj[0]]) + "].combox_input[" + \
                              str(i) + "].get())], "
                        
                        # Choose correct scalar type DataObject based on selected 
                        # name
                        else:
                            exec_line += "=self.vals[self.val_names.index(" + \
                              "self.select_name[" + str(counts[obj[0]]) + \
                              "].combox_input[" + str(i) + "].get())], "
                    
                else:
                    exec_line += obj[1][0]
                
                    # Choose correct array type DataObject based on selected 
                    # name
                    if obj[3]:
                        exec_line += "=self.ranges[self.rng_names.index(" +\
                          "self.select_name[" + str(counts[obj[0]]) + \
                          "].combox_input.get())], "
                    
                    # Choose correct scalar type DataObject based on selected 
                    # name
                    else:
                        exec_line += "=self.vals[self.val_names.index(" +\
                          "self.select_name[" + str(counts[obj[0]]) + \
                          "].combox_input.get())], "
                
                # Define outputs
                if not isinstance(obj[1][1], str):
                    for i, item in enumerate(obj[1][1]):
                        exec_line += item + "=self.select_name[" + \
                          str(counts[obj[0]]) + "].entry_input[" + str(i) + \
                          "].get(), "
                        exec_line += obj[1][2][i] + "=self.select_name[" + \
                          str(counts[obj[0]]) + "].db_flag[" + str(i) + \
                          "].get(), "
                else:
                    exec_line += obj[1][1] + "=self.select_name[" + \
                      str(counts[obj[0]]) + "].entry_input.get(), "
                    exec_line += obj[1][2] + "=self.select_name[" + \
                      str(counts[obj[0]]) + "].db_flag.get(), "
            
            counts[obj[0]] += 1
            
        exec_line = exec_line[:-2]
        exec_line += ")"
        
        # Create calc object instance and add to local namespace
        exec(exec_line, globals(), ldict)
        data_uncomm = ldict['data_uncomm']
        
        # Check calc inputs before committing to the analysis
        check_str = data_uncomm.check()
        
        if check_str != None:
            messagebox.showerror(
                "User Input Error",
                check_str,
                parent=self)
            return None
        
        # Check output names for uniqueness
        for obj in data_uncomm.outputs:
            if not self.data_ref.output_check(obj.name, self.i):
                messagebox.showerror(
                    "Output Name Conflict",
                    "Output name '" + str(obj.name) + "' already exists.",
                    parent=self)
                return None
        
        # Add new calc instance to the analysis data container
        if self.i == None:
            self.data_ref.calcs.append(data_uncomm)
            self.data_ref.outputs.extend(data_uncomm.outputs)
        
        # Handle edit of existing calc
        else:
            # Replace old output references in subsequent calcs
            for calc in self.data_ref.calcs[self.i+1:]:
                for i, output in enumerate(self.data_ref.calcs[self.i].outputs):
                    for item in calc.__dict__.keys():
                        if calc.__dict__[item] == output:
                            calc.__dict__[item] = data_uncomm.outputs[i]
            
            # Replace old calc outputs with updated calc outputs
            for i, obj in enumerate(self.data_ref.calcs[self.i].outputs):
                self.data_ref.outputs.remove(obj)
                self.data_ref.outputs.insert(i, data_uncomm.outputs[i])
            
            # Replace parent/child references to new calc
            self.data_ref.calcs[self.i].switcheroo(data_uncomm)
            
            # Replace old calc with updated calc
            del self.data_ref.calcs[self.i]
            self.data_ref.calcs.insert(self.i, data_uncomm)
            
        self.display.update_data()
        self.display.reconcile_lines()
        self.destroy()

def run_calc(dataset):
    
    # Standalone static method that is called by the multiprocessing
    # pool function
    
    key = dataset.inputs[0].path + "\\" + dataset.inputs[0].name
    
    # Run calc queue for a single dataset
    for calc in dataset.calcs:
        
        # If the process interacts with input files, set the
        # path per the current dataset
        if type(calc).__name__ in ["ValFromTemplate", 
                                   "RngFromTemplate"]:
            for tail in dataset.inputs[0].tails:
                if calc.suffix == tail[0:len(calc.suffix)]:
                    calc.path = key + str(tail)
                    
        calc.run()
    
    return key, dataset.outputs