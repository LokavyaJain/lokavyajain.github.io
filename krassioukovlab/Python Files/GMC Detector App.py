# File Generated on February 21, 2026
# This is an app to optimize GMC detection per animal by tweaking various parameters 

import os
import pandas as pd
import numpy as np
from scipy import signal, ndimage
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.colors as mcolors
import json

class PipelineGUI:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

        all_csvs = [f for f in os.listdir(folder_path) if f.endswith('.csv') and not f.startswith('.')]
        
        # 2. Filter the files before adding them to the app
        self.files_list = []
        for file_name in all_csvs:
            # Run the file name through your existing parser
            attrs = self.non_Stim_Name_Attribute_Collector(file_name)
            
            # attrs is: (animal_ID, depth, volume, injury, time)
            
            # If you set a filter, and the file doesn't match it, skip to the next file
            #if attrs[1] != : continue #target_depth
            #if attrs[2] != : continue #target_volume 
            #if attrs[3] != "Transection": continue #target_injury
            if attrs[4] != "Week 5": continue #target_time
            
            # If it survives all the checks, add it to the list!
            self.files_list.append(file_name)

        self.current_index = 0  
        
        # Data holders
        self.time_Data_X = None
        self.background_trace = None 
        self.current_attributes = {}
        
        print(f"System Initialized. Found {len(self.files_list)} CSV files.")

    def non_Stim_Name_Attribute_Collector(self, file_path: str):
        slashes_Index = [x for (x, y) in enumerate(file_path) if y == "/"]
        first_Index = max(slashes_Index) if slashes_Index else -1
        file_Name = file_path[first_Index+1:]
        
        underscore_Index = [x for (x, y) in enumerate(file_Name) if y == "_"]
        if len(underscore_Index) < 3:
            return ("Unknown", "Unknown", "Unknown", "Unknown", "Unknown")

        animal_ID = file_Name[:underscore_Index[0]]
        depth = file_Name[underscore_Index[0]+1:underscore_Index[1]]
        volume = file_Name[underscore_Index[1]+1:underscore_Index[2]]
        injury = file_Name[underscore_Index[2]+1:underscore_Index[3]]
        
        dot_index = file_Name.find('.csv')
        time = file_Name[underscore_Index[3]+1:dot_index]

        if animal_ID.startswith("."): return "File starts with period"
        if injury == "TRANS": injury = "Transection"
        if injury == "CONT": injury = "Contusion"
        if injury == "PREI": injury = "Pre-Injury"
        if time in ["1wk", "wk1"]: time = "Week 1"
        if time in ["2wk", "wk2"]: time = "Week 2"
        if time in ["3wk", "wk3"]: time = "Week 3"
        if time in ["4wk", "wk4"]: time = "Week 4"
        if time in ["5wk", "wk5"]: time = "Week 5"
        if time in ["6wk", "wk6"]: time = "Week 6"
        if time in ["0hr", "24h", "24hr"]: time = "Day 1"
        if time == "pre": time = "Pre-Injury"
        
        return (animal_ID, depth, volume, injury, time)

    def prep_Function(self):
        file_name = self.files_list[self.current_index]
        file_path = os.path.join(self.folder_path, file_name)
        
        attrs = self.non_Stim_Name_Attribute_Collector(file_path)
        self.current_attributes = {
            'animal_ID': attrs[0], 'depth': attrs[1], 
            'volume': attrs[2], 'injury': attrs[3], 'time': attrs[4]
        }
        
        print(f"\nLoading: {file_name}")
        
        data_Frame = pd.read_csv(file_path)
        raw_time = data_Frame['Time_s'].values
        raw_pressure = data_Frame['Pressure_mmHg'].values
        
        raw_time = raw_time - raw_time[0]
        
        pressure_100Hz = signal.decimate(raw_pressure, q=10)
        self.background_trace = signal.decimate(pressure_100Hz, q=10)
        
        self.time_Data_X = raw_time[::100] 
        
        min_length = min(len(self.time_Data_X), len(self.background_trace))
        self.time_Data_X = self.time_Data_X[:min_length]
        self.background_trace = self.background_trace[:min_length]
        
        self.background_trace = signal.detrend(self.background_trace, type='linear')
        b, a = signal.butter(4, 1, btype='lowpass', fs=10)
        self.background_trace = signal.filtfilt(b, a, self.background_trace, padtype='even')

    def run_Engine(self, savgol_1_win, polyorder_1, skyline_win, savgol_2_win, polyorder_2, prom_val, rel_h_val, min_width):
        polyorder_1, polyorder_2 = int(polyorder_1), int(polyorder_2)
        savgol_1_win, savgol_2_win, skyline_win = int(savgol_1_win), int(savgol_2_win), int(skyline_win)
        
        if savgol_1_win % 2 == 0: savgol_1_win += 1
        if savgol_2_win % 2 == 0: savgol_2_win += 1
        
        if savgol_1_win <= polyorder_1: 
            savgol_1_win = polyorder_1 + 1 if (polyorder_1 + 1) % 2 != 0 else polyorder_1 + 2
        if savgol_2_win <= polyorder_2: 
            savgol_2_win = polyorder_2 + 1 if (polyorder_2 + 1) % 2 != 0 else polyorder_2 + 2

        trace = self.background_trace.copy()

        trace = signal.savgol_filter(trace, window_length=savgol_1_win, polyorder=polyorder_1)
        trace = ndimage.maximum_filter1d(trace, size=skyline_win)
        trace = signal.savgol_filter(trace, window_length=savgol_2_win, polyorder=polyorder_2)
        
        peaks, properties = signal.find_peaks(
            trace, prominence=prom_val, rel_height=rel_h_val, width=min_width
        )
        
        self.current_peaks = peaks
        self.current_starts = np.round(properties['left_ips']).astype(int)
        self.current_ends = np.round(properties['right_ips']).astype(int)
        
        return len(peaks)
    
    def build_GUI(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        plt.subplots_adjust(bottom=0.5) 
        
        t = self.current_attributes
        title_str = f"{t['animal_ID']} {t['depth']} {t['volume']} {t['injury']} {t['time']}"
        self.ax.set_title(title_str, fontsize=14, fontweight='bold')
        self.ax.set_ylabel("Pressure (mmHg)")
        self.ax.set_xlabel("Time (s)")

        self.main_line, = self.ax.plot(self.time_Data_X, self.background_trace, color='black', linewidth=1.2)
        self.mask_collection = [] 

        ax_sav1   = plt.axes([0.15, 0.40, 0.65, 0.02])
        ax_poly1  = plt.axes([0.15, 0.36, 0.65, 0.02])
        ax_sky    = plt.axes([0.15, 0.32, 0.65, 0.02])
        ax_sav2   = plt.axes([0.15, 0.28, 0.65, 0.02])
        ax_poly2  = plt.axes([0.15, 0.24, 0.65, 0.02])
        ax_prom   = plt.axes([0.15, 0.16, 0.65, 0.02]) 
        ax_relh   = plt.axes([0.15, 0.12, 0.65, 0.02])
        ax_width  = plt.axes([0.15, 0.08, 0.65, 0.02])

        self.s_sav1   = Slider(ax_sav1, 'Savgol 1 Win', 3, 201, valinit=75, valstep=2)
        self.s_poly1  = Slider(ax_poly1, 'Savgol 1 Poly', 1, 3, valinit=2, valstep=1)
        self.s_sky    = Slider(ax_sky, 'Skyline Win', 5, 300, valinit=75, valstep=1)
        self.s_sav2   = Slider(ax_sav2, 'Savgol 2 Win', 3, 201, valinit=101, valstep=2)
        self.s_poly2  = Slider(ax_poly2, 'Savgol 2 Poly', 1, 3, valinit=1, valstep=1)
        self.s_prom   = Slider(ax_prom, 'Prominence', 1.0, 50.0, valinit=10.0, valstep=0.5)
        self.s_relh   = Slider(ax_relh, 'Rel Height', 0.5, 1.0, valinit=0.95, valstep=0.01)
        self.s_width  = Slider(ax_width, 'Min Width', 0, 300, valinit=0, valstep=1)

        ax_prev = plt.axes([0.15, 0.02, 0.1, 0.04])
        ax_save = plt.axes([0.425, 0.02, 0.15, 0.04])
        ax_next = plt.axes([0.7, 0.02, 0.1, 0.04])

        self.btn_prev = Button(ax_prev, 'Previous File')
        self.btn_save = Button(ax_save, 'SAVE DATA', color='lightgreen')
        self.btn_next = Button(ax_next, 'Next File')

        def update(val):
            self.run_Engine(
                self.s_sav1.val, self.s_poly1.val, self.s_sky.val, 
                self.s_sav2.val, self.s_poly2.val, 
                self.s_prom.val, self.s_relh.val, self.s_width.val
            )
            for mask in self.mask_collection: mask.remove()
            self.mask_collection.clear()
            
            colors = list(mcolors.TABLEAU_COLORS.values())
            for i in range(len(self.current_starts)):
                if self.current_starts[i] < len(self.time_Data_X) and self.current_ends[i] < len(self.time_Data_X):
                    start_time = self.time_Data_X[self.current_starts[i]]
                    end_time = self.time_Data_X[self.current_ends[i]]
                    c = colors[i % len(colors)]
                    mask = self.ax.axvspan(start_time, end_time, color=c, alpha=0.3)
                    self.mask_collection.append(mask)
            self.fig.canvas.draw_idle()

        for slider in [self.s_sav1, self.s_poly1, self.s_sky, self.s_sav2, self.s_poly2, self.s_prom, self.s_relh, self.s_width]:
            slider.on_changed(update)

        def change_file():
            self.prep_Function() 
            self.main_line.set_data(self.time_Data_X, self.background_trace)
            self.ax.relim()          
            self.ax.autoscale_view() 
            
            t = self.current_attributes
            self.ax.set_title(f"{t['animal_ID']} {t['depth']} {t['volume']} {t['injury']} {t['time']}", fontsize=14, fontweight='bold')
            update(None) 

        def next_file(event):
            if self.current_index < len(self.files_list) - 1:
                self.current_index += 1
                change_file()
            else:
                print("Already at the last file.")

        def prev_file(event):
            if self.current_index > 0:
                self.current_index -= 1
                change_file()
            else:
                print("Already at the first file.")

        def save_data(event):
            attrs = self.current_attributes
            file_key = f"{attrs['animal_ID']}_{attrs['depth']}_{attrs['volume']}_{attrs['injury']}_{attrs['time']}"
            
            new_rows = []
            for i in range(len(self.current_peaks)):
                new_rows.append({
                    'animal_ID': attrs['animal_ID'], 'depth': attrs['depth'],
                    'volume': attrs['volume'], 'injury': attrs['injury'],
                    'time': attrs['time'],
                    'peak_index': int(self.current_peaks[i] * 100), 
                    'start_index': int(self.current_starts[i] * 100),
                    'end_index': int(self.current_ends[i] * 100)
                })
            
            if len(new_rows) == 0:
                new_rows.append({
                    'animal_ID': attrs['animal_ID'], 'depth': attrs['depth'],
                    'volume': attrs['volume'], 'injury': attrs['injury'],
                    'time': attrs['time'],
                    'peak_index': None, 'start_index': None, 'end_index': None
                })
                
            new_df = pd.DataFrame(new_rows)

            csv_path = os.path.join(self.folder_path, "GMC_Output.csv")
            if os.path.exists(csv_path):
                master_df = pd.read_csv(csv_path)
                mask = ~((master_df['animal_ID'] == attrs['animal_ID']) &
                         (master_df['depth'] == attrs['depth']) &
                         (master_df['volume'] == attrs['volume']) &
                         (master_df['injury'] == attrs['injury']) &
                         (master_df['time'] == attrs['time']))
                master_df = master_df[mask]
                master_df = pd.concat([master_df, new_df], ignore_index=True)
            else:
                master_df = new_df
                
            master_df.to_csv(csv_path, index=False)

            json_path = os.path.join(self.folder_path, "GMC_Params.json")
            params = {}
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    params = json.load(f)
            
            params[file_key] = {
                'savgol_1_win': int(self.s_sav1.val * 100), 
                'polyorder_1': self.s_poly1.val,
                'skyline_win': int(self.s_sky.val * 100),
                'savgol_2_win': int(self.s_sav2.val * 100), 
                'polyorder_2': self.s_poly2.val,
                'prominence': self.s_prom.val, 
                'rel_height': self.s_relh.val, 
                'min_width': int(self.s_width.val * 100)
            }
            with open(json_path, 'w') as f:
                json.dump(params, f, indent=4)
                
            print(f"SUCCESS: Saved data for {file_key}.")

        self.btn_next.on_clicked(next_file)
        self.btn_prev.on_clicked(prev_file)
        self.btn_save.on_clicked(save_data)

        update(None) 
        plt.show()

# ==========================================
# EXECUTION BLOCK (How to Run It)
# ==========================================
if __name__ == "__main__":
    # 1. Provide your folder path here
    DATA_FOLDER = '/Volumes/KINGSTON/ContusionAnimal_Project/All Raw Data' 
    
    # 2. Initialize the App
    app = PipelineGUI(DATA_FOLDER)
    
    # 3. Start the process
    if len(app.files_list) > 0:
        app.prep_Function() # Load the first file
        app.build_GUI()     # Open the interactive window
    else:
        print(f"No CSV files found in {DATA_FOLDER}. Please check the path.")