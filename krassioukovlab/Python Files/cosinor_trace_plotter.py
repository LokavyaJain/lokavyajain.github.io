#This script will plot the raw cosinor data with new figures 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os 


df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/COSINOR/Data/Full Cosinor Analysis.csv')

columns = df.columns.to_list()

list_of_dictionaries = df.to_dict('records')

for x in list_of_dictionaries:
    dict = x
    time_data = ast.literal_eval(dict["time_data"])
    bp_values = ast.literal_eval(dict["bp_values"])
    plt.figure(figsize = (5, 2.5))
    plt.scatter(time_data, bp_values, color = "black", s=10)

    t_plot = ast.literal_eval(dict["t_plot"])
    fitted_wave = ast.literal_eval(dict["fitted_wave"])
    plt.plot(t_plot, fitted_wave, color = "black", linewidth = 2)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)  
    plt.savefig(f'/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/COSINOR/Cosinor Plots/{dict["Participant"]}_{dict["Intervention"]}', dpi = 200)




    

pre_acro = []
post_acro = []
for x in list_of_dictionaries:
    dict = x
    acrophase = (dict['MESOR'])
    print(acrophase)
    
    if dict["Intervention"] == "Pre":
        pre_acro.append(acrophase)
    else:
        post_acro.append(acrophase)

print(np.mean(pre_acro), np.mean(post_acro))
    


print(columns)