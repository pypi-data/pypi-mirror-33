"""
LED_Analyze - main
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
from analysis_main import *
from gui_main import *

def configure(event):
    
    # Adjust frame heights based on window resize    
    if analysis_gui is event.widget:
        total_hgt = event.height
        frame_hgt = int((total_hgt - 448) / 3)
    
        analysis_gui.temp_frame.scrframe.canvas.configure(
            height = frame_hgt)
        analysis_gui.input_frame.scrframe.canvas.configure(
            height = frame_hgt)
        analysis_gui.calc_frame.scrframe.canvas.configure(
            height = frame_hgt)

if __name__ == '__main__':
    analysis_data = Analysis()
    
    analysis_gui = MainGUI(analysis_data)
    analysis_gui.resizable(False, True)
    analysis_gui.minsize(height=825)
    
    analysis_gui.bind("<Configure>", configure)
    
    analysis_gui.mainloop()