#This is a python script to produce a consinor regression for 10 participants (listed below).
#The participant list is update after the new percentage qualification

import pandas as pd
import numpy as np
import statsmodels.api as sm
import math

def perform_cosinor(participant: str, intervention: str,time_hours: list, bp_values: list):

    #Turning them into numpy to do the full vector multiplication 
    time_hours = np.array(time_hours)
    bp_values = np.array(bp_values)

    # 1. Define frequency (24-hour period)
    omega = 2 * np.pi / 24
    
    # 2. Create the features based on raw ABPM timepoints
    X1 = np.cos(omega * time_hours)
    X2 = np.sin(omega * time_hours)
    
    # 3. Create the design matrix
    X = pd.DataFrame({'MESOR': 1, 'beta1': X1, 'beta2': X2})
    
    # 4. Fit the Ordinary Least Squares (OLS) model
    model = sm.OLS(bp_values, X).fit()
    
    # 5. Extract resulting coefficients
    M = model.params['MESOR']
    b1 = model.params['beta1']
    b2 = model.params['beta2']
    
    # 6. Calculate Circadian Parameters
    amplitude = np.sqrt(b1**2 + b2**2)
    phi_rad = np.arctan2(b2, b1)
    acrophase_hrs = (phi_rad * 24 / (2 * np.pi)) % 24
    
    # ---------------------------------------------------------
    # 7. GENERATE SMOOTH PLOTTING ARRAYS
    # ---------------------------------------------------------
    # Dynamically match the start and end times of the unwrapped data
    t_plot = np.linspace(np.min(time_hours), np.max(time_hours), 100)
    
    cos_comp = b1 * np.cos(omega * t_plot)
    sin_comp = b2 * np.sin(omega * t_plot)
    fitted_wave = M + cos_comp + sin_comp

    return {
        #Participant Details 
        "Participant": participant,
        "Intervention": intervention,

        # Clinical Statistics
        "MESOR": M,
        "Amplitude": amplitude,
        "Acrophase_Hrs": acrophase_hrs,
        "P_Value": model.f_pvalue,
        
        # Raw Mathematical Coefficients
        "beta1": b1,
        "beta2": b2,
        "omega": omega,
        
        # Smooth Arrays for Matplotlib (Use .tolist() to convert np.float64 to native Python floats)
        "t_plot": t_plot.tolist(),               
        "cos_component": cos_comp.tolist(),      
        "sin_component": sin_comp.tolist(),      
        "fitted_wave": fitted_wave.tolist(),      

        # Original data in an easily graphable format
        "time_data": time_hours.tolist(),
        "bp_values": bp_values.tolist()
    }

#The list of the 10 included participants
participant_IDs = ["ISRT01", "ISRT02", "ISRT04", "ISRT05", "ISRT06", "ISRT07", "ISRT16", "ISRT20", "DOD08", "DOD17"]

#Getting the long form CSV and turning that into a pandas dataframe
df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/All Participant Raw Data Long Form.csv')
df = df[df['Participant'].isin(participant_IDs)]

df_list = [group for _, group in df.groupby(['Participant', 'Intervention'])]
print(df_list)

participant_Data_List = []

for x in df_list:
    single_Participant_DF = x 
    single_Participant_DF = single_Participant_DF.dropna(subset=['Time', 'DBP'])

    # 1. Convert HH:MM string to raw fractional hours (e.g., 14:30 -> 14.5)
    raw_hours = pd.to_datetime(single_Participant_DF['Time'], format='%H:%M').dt.hour + \
                pd.to_datetime(single_Participant_DF['Time'], format='%H:%M').dt.minute / 60
    
    single_Participant_DF['Time'] = raw_hours
    '''
    # 2. Detect midnight rollovers to create a continuous time vector
    # .diff() calculates the difference from the previous row. 
    # A negative drop (e.g., 23.5 -> 0.5) flags a midnight crossing.
    # .cumsum() counts how many times midnight has been crossed up to that row.
    rollovers = (raw_hours.diff() < 0).cumsum()
    
    # 3. Add 24 hours for every midnight crossed to prevent the time from resetting
    single_Participant_DF['Time'] = raw_hours + (rollovers * 24)
'''
    participant = single_Participant_DF["Participant"].to_list()
    participant = list(set(participant))[0]

    pre_post = single_Participant_DF["Intervention"].to_list()
    pre_post = list(set(pre_post))[0]

    time_hours = single_Participant_DF["Time"].to_list()
    bp_values = single_Participant_DF["DBP"].to_list()

    print(time_hours, bp_values)

    #reordering the measurments
    time_hours = np.array(time_hours)
    bp_values = np.array(bp_values)
    indices = np.argsort(time_hours)
    sorted_hours = time_hours[indices]
    sorted_values = bp_values[indices]
    time_hours = sorted_hours.tolist()
    bp_values = sorted_values.tolist()

    
    print(time_hours, bp_values)

    print()
    print()
    print()
    print()

    value_Dict = perform_cosinor(participant, pre_post, time_hours, bp_values)

    participant_Data_List.append(value_Dict)
    

final_df = pd.DataFrame(participant_Data_List)

save_path = '/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/COSINOR/Data/Full Cosinor Analysis DBP.csv'

final_df.to_csv(save_path, index = False)

print(f"Data saved successfully to: {save_path}")
