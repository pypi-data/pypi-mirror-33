"""
LED_Analyze - gui_common
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Combobox
from collections import Iterable

class VerticalScrolledFrame(Frame):
    """
    Vertically scrollable frame for tkinter window
    """
    def __init__(self, parent, hgt, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # Create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.grid(row=0, column=1, sticky=N+S)
        self.canvas = Canvas(
            self, 
            bd=0, 
            highlightthickness=0, 
            height=hgt,
            yscrollcommand=vscrollbar.set)
        self.canvas.grid(row=0, column=0)
        vscrollbar.config(command=self.canvas.yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(
            0, 0, window=interior, anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            
            # Update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(
                    interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

class SelectableScrFrame(VerticalScrolledFrame):
    """
    Vertically Scrolling Frame displaying data lines with radio buttons. 
    The frame displays relevant data for review and allows selection for 
    editing and removal operations.
    """
    def __init__(self, master, data_ref, header, height):
        
        # Create Scrollable Frame
        VerticalScrolledFrame.__init__(self, master, height)
        self.config(borderwidth=1, relief=SUNKEN)
        
        # initialize attributes
        self.master = master
        self.data_ref = data_ref
        self.header = header
        self.data_lines = []
        self.wdgt_lines = []
        self.sel_line = IntVar(value=None)
        
        # Grid Setup and header labels
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        for i, value in enumerate(header):
            
            self.interior.columnconfigure(
                i, minsize=value[1])
            
            Label(
                self.interior,
                text=value[0],
                borderwidth=1,
                relief=GROOVE
                ).grid(row=0, column=i, sticky=W+E)
        
    def reconcile_lines(self, start=0):
        
        # Update the displayed lines of widgets to match the data_lines container
        
        for line in self.wdgt_lines[start:]:
            for wdgt in line:
                wdgt.destroy()
        
        self.wdgt_lines = self.wdgt_lines[:start]
                        
        for i, line in enumerate(self.data_lines[start:], start):
            new_line = []
            new_line.append(
                Radiobutton(self.interior,
                            variable=self.sel_line, 
                            value=i))
            new_line[0].grid(row=i+1, column=0)
            
            for j, item in enumerate(line, 1):
                new_line.append(
                    Label(self.interior,
                          text=item, 
                          wraplength=self.header[j][1]-10))
                new_line[j].grid(row=i+1, column=j)
            
            self.wdgt_lines.append(new_line)
    
class FileInputFrame(Frame):
    """
    GUI element containing a button that initiates an open file dialog
    and a display showing the currently selected path.
    """
    def __init__(self, master, wdt, file_type):
        
        # Create and configure frame
        Frame.__init__(self, master)
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, minsize=wdt-60)
        self.columnconfigure(2, minsize=75)
        self.columnconfigure(3, minsize=5)
        
        # Initialize attributes
        self.master = master
        self.path = StringVar()
        self.file_type = file_type
        
        # Create widgets
        Label(
            self,
            text="Input File:"). grid(
                row=1, column=1, sticky=W)
        
        self.display = Entry(
            self,
            state="readonly",
            textvariable=self.path)
        self.display.grid(
            row=2, column=1, padx=5, sticky=W+E)
        
        Button(
            self,
            text="Browse",
            width=8,
            command=self.get_file).grid(
                row=2, column=2)
    
    def get_file(self):
        
        if self.file_type == "Delimited Text":
            open_types = (
                ("Delimited Text Files", "*.txt"),
                ("Delimited Text Files", "*.csv"))
        elif self.file_type == "Spreadsheet":
            open_types = (
                ("Excel Files", "*.xls"),
                ("Excel Files", "*.xlsx"),
                ("Excel Files", "*.xlsm"))
        elif self.file_type == "Image":
            open_types = (
                ("Bitmap Image", "*.bmp"),
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"))
        
        self.path.set(filedialog.askopenfilename(
            initialdir="C:\\",
            title="Select an input data file",
            filetypes=open_types,
            parent=self.master))

class CheckEntryFrame(Checkbutton):
    """
    GUI element with a true/false toggle and self contained BooleanVar
    """
    def __init__(self, master, label):
        self.flag = BooleanVar()
        Checkbutton.__init__(self, master, text=label, variable=self.flag)

class TextEntryFrame(Frame):
    """
    GUI element containing a text entry frame and a label.
    """
    def __init__(self, master, label, wdt, lbl_wdt=0):
        
        # Create and configure frame
        Frame.__init__(self, master)
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, minsize=lbl_wdt)
        self.columnconfigure(2, minsize=wdt-lbl_wdt-10)
        self.columnconfigure(3, minsize=5)
        
        # Initialize attributes
        self.entry_input = StringVar()
        
        # Create widgets
        Label(
            self,
            text=label,
            wraplength=lbl_wdt). grid(
                row=1, column=1, sticky=W)
        
        self.field = Entry(
            self,
            width=2,
            textvariable=self.entry_input)
        self.field.grid(row=1, column=2, sticky=W+E)
    
    def enable(self):
        self.field.config(state="normal")
        
    def disable(self):
        self.entry_input.set("")
        self.field.config(state=DISABLED)

class SpboxFrame(Frame):
    """
    GUI element containing a spinbox and a label.
    """
    def __init__(self, master, label, vals, wdt, lbl_wdt=0):
        
        # Create and configure frame
        # Create and configure frame
        Frame.__init__(self, master)
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, minsize=lbl_wdt)
        self.columnconfigure(2, minsize=wdt-lbl_wdt-10)
        self.columnconfigure(3, minsize=5)
        
        # Initialize attributes
        self.spbox_input = StringVar()
        
        # Create widgets
        Label(
            self,
            text=label). grid(
                row=1, column=1, sticky=W)
        
        Spinbox(
            self,
            width=2,
            textvariable=self.spbox_input,
            values=vals,
            state="readonly").grid(
                row=1, column=2, sticky=W+E)

class ComboboxFrame(Frame):
    """
    GUI element containing a combobox and a label.
    """
    def __init__(self, master, label, vals, wdt, lbl_wdt=0):
        
        Frame.__init__(self, master)
        
        self.rowconfigure(0, minsize=5)
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, minsize=lbl_wdt)
        self.columnconfigure(2, minsize=wdt-lbl_wdt-10)
        self.columnconfigure(3, minsize=5)
        
        # Initialize attributes
        self.combox_input = StringVar()
        
        # Create widgets
        Label(
            self,
            text=label). grid(
                row=1, column=1, sticky=W)
        
        self.combox = Combobox(
            self,
            width=2,
            textvariable=self.combox_input,
            values=vals,
            state="readonly")
        self.combox.grid(
            row=1, column=2, sticky=W+E)
    
class SelectNameLabelFrame(LabelFrame):
    """
    GUI element with a selection Combobox and name entry frame
    inside of a LabelFrame.
    """
    def __init__(self, master, vals, select_lbl, 
                 text_lbl, title, wdt, lbl_wdt=0):
        
        LabelFrame.__init__(self, master)
        
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(4, minsize=5)
        self.configure(text=title)
        
        # Implicit conversion to equally weighted list if single
        # value for lbl_wdt is given
        if not isinstance(lbl_wdt, Iterable):
            lbl_wdt = (lbl_wdt, lbl_wdt)
        
        # Create input widgets if input implies group of inputs
        if not isinstance(vals[0], str):
            self.select_in = []
            self.combox_input = []
            
            for i, subvals in enumerate(vals):
                self.select_in.append(ComboboxFrame(
                    self,
                    select_lbl[i],
                    subvals,
                    (wdt - 10) / 2, lbl_wdt[0]))
                self.select_in[i].grid(
                    row=1+i, column=1, sticky= W)
                self.combox_input.append(
                    self.select_in[i].combox_input)
                
        # Or if it's a single input
        else:
            self.select_in = ComboboxFrame(
                self,
                select_lbl,
                vals,
                (wdt - 10) / 2, lbl_wdt[0])
            self.select_in.grid(
                row=1, column=1, sticky=W)
            self.combox_input = self.select_in.combox_input
        
        # Create output widgets if input implies group
        if not isinstance(text_lbl, str):
            self.text_in = []
            self.entry_input = []
            self.check_in = []
            self.db_flag = []
            
            for i, lbl in enumerate(text_lbl):
                self.text_in.append(TextEntryFrame(
                    self,
                    lbl,
                    (wdt-10) / 2, lbl_wdt[1]))
                self.text_in[i].grid(
                    row=1+i, column=2, sticky=W)
                self.entry_input.append(
                    self.text_in[i].entry_input)
                
                self.check_in.append(CheckEntryFrame(
                    self,
                    "Save To DB?"))
                self.check_in[i].grid(
                    row=1+i, column=3, sticky=W)
                self.db_flag.append(self.check_in[i].flag)
                
        # Or if it is a single output
        else:
            self.text_in = TextEntryFrame(
                self,
                text_lbl,
                (wdt - 10) / 2, lbl_wdt[1])
            self.text_in.grid(
                row=1, column=2, sticky=W)
            self.entry_input = self.text_in.entry_input
            
            self.check_in = CheckEntryFrame(
                self,
                "Save To DB?")
            self.check_in.grid(
                row=1, column=3, sticky=W)
            self.db_flag = self.check_in.flag
                
        self.rowconfigure(2, minsize=5)
        
        