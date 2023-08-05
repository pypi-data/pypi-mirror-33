"""
LED_Analyze - db
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
import sqlite3 as sq
from os.path import splitext
import io
import numpy as np
import codecs

class AnalysisDatabase:
    """
    Object that creates, modifies, and reads from an sqlite3 database.
    This allows calculated data to be stored in on the disk, rather than
    in memory, so that many data sets can be calculated at once and then
    output to human-readable format as a group.
    """
    def __init__(self, sqlite_file):
        
        # Register numpy array handler so that numpy arrays may
        # be stored in the database as binary blobs
        sq.register_adapter(np.ndarray, self.adapt_array)
        sq.register_converter("array", self.convert_array)
        
        # Initialize and create database
        self.conn = sq.connect(sqlite_file,
                               detect_types=sq.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS data_table (
                id TEXT PRIMARY KEY
            ); """)
    
    def get_data_headers(self):
        
        # Get the names of data table columns (corresponding to 
        # calculation outputs with the 'save to DB' flag.
        self.cursor.execute(
            "SELECT * FROM data_table")
        return [header[0] for header in self.cursor.description]
    
    def get_keys(self):
        
        # Get names of data sets processed by the calculations
        self.cursor.execute(
            "SELECT id FROM data_table")
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_data_column(self, header, data_type):
        
        if data_type == "Scalar":
            type_name = "TEXT"
        elif data_type == "Array":
            type_name = "array"
        
        try:
            self.cursor.execute(
                "ALTER TABLE data_table ADD COLUMN {cn} {dt}"\
                .format(cn=header, dt=type_name))
        
        except sq.IntegrityError:
            print("Column already exists")
    
    def add_row(self, id):
        
        self.cursor.execute(
            "INSERT OR IGNORE INTO data_table (id) VALUES (?)", (id,))
    
    def insert_val(self, name, header, val):
        
        key = quote_identifier(name)
        self.cursor.execute(
            "UPDATE data_table SET {cn}=(?) WHERE id=({target})".\
            format(cn=header, target=key), (val,))
    
    def get_val(self, name, header):
        
        key = quote_identifier(name)
        type = self.get_col_type(header)
        
        self.cursor.execute(
            "SELECT {cn} FROM data_table WHERE id=({target})".\
            format(cn=header, target=key))
        if type == "Scalar":
            return self.numberify(self.cursor.fetchall()[0][0])
        else:
            return self.cursor.fetchone()[0]
    
    def get_col_type(self, name):
        
        self.cursor.execute(
            "PRAGMA TABLE_INFO(data_table)")
        info = self.cursor.fetchall()
        
        for item in info:
#             print((item[1], name, item[1] == name))
            if item[1] == name:
                if item[2] == 'array':
                    return "Array"
                else:
                    return "Scalar"
    
    def reconcile_data_headers(self, headers):
        
        # Check if the data table column names match the input header list
        # If not, add missing columns and NULL out superfluous columns
        curr_headers = self.get_data_headers()
        
        for i, header in enumerate(headers[0]):
            if header not in curr_headers:
                self.add_data_column(header, headers[1][i].type)
                
        for header in curr_headers:
            if header not in headers[0] + ["id"]:
                for key in self.get_keys():
                    self.insert_val(key, header, None)

    def reconcile_data_rows(self, keys):
        
        # Check if the data table row keys (i.e. data set names)
        # match the input data set names. If not, add missing rows
        # and NULL out superfluous rows.
        curr_keys = self.get_keys()
        curr_data_headers = list(self.get_data_headers())
        curr_data_headers.remove("id")
        
        for key in keys:
            if key not in curr_keys:
                self.add_row(key)
        
        for key in curr_keys:
            if key not in keys:
                for header in curr_data_headers:
                    self.insert_val(key, header, None)

    @staticmethod
    def adapt_array(arr):
        # Source: stackoverflow - SoulNibbler
        # http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
        
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sq.Binary(out.read())
    
    @staticmethod
    def convert_array(text):
        # Source: stackoverflow - SoulNibbler
        # http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
        
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)
    
    def close(self):
        self.conn.commit()
        self.conn.close()
        
    @staticmethod
    def numberify(y):
        if y == None:
            return y
        try:
            test1 = float(y)
            test2 = int(test1)
            return test2 if test1 == test2 else test1
        except ValueError:
            try:
                return float(y)
            except ValueError:
                return y

def quote_identifier(s, errors="strict"):
    # Fix identifier string to make it usable as sqlite identifier
    # Source: stackoverflow - user1114 
    # https://goo.gl/aWZ14w
    
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""