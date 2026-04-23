#This file will plot pre and post 24-hour ambulatory blood pressure data 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def preprocess_data(df):
    """
    Cleans the data by coercing empty strings to NaNs and building a 
    continuous datetime axis to prevent midnight crossover loops.
    """
    df['SBP'] = pd.to_numeric(df['SBP'], errors='coerce')
    df['DBP'] = pd.to_numeric(df['DBP'], errors='coerce')
    df['BPM'] = pd.to_numeric(df['BPM'], errors='coerce')

    datetimes = []
    current_date = datetime(2000, 1, 1)
    last_time = None
    
    # Trackers to reset the dummy date for every phase
    last_participant = None
    last_phase = None

    for idx, row in df.iterrows():
        # Reset the date tracker if we switch to a new participant or a new phase
        if row['Participant'] != last_participant or row['Intervention'] != last_phase:
            current_date = datetime(2000, 1, 1)
            last_time = None
            last_participant = row['Participant']
            last_phase = row['Intervention']

        time_str = str(row['Time']).strip()
        try:
            t = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            datetimes.append(pd.NaT)
            continue

        if last_time is not None:
            if t < last_time:
                current_date += timedelta(days=1)

        dt = datetime.combine(current_date.date(), t)
        datetimes.append(dt)
        last_time = t

    df['Continuous_Time'] = datetimes
    return df

def calculate_statistics(df_participant):
    """
    Calculates Min, Max, separated Outliers, CV, and ARV for Pre and Post phases.
    """
    stats = {}
    for phase in ['Pre', 'Post']:
        phase_df = df_participant[df_participant['Intervention'] == phase]
        sbp = phase_df['SBP'].dropna()

        if len(sbp) == 0:
            stats[phase] = {
                'Min SBP': 'N/A', 'Max SBP': 'N/A',
                'Outliers Total': 'N/A', 'Outliers > 150': 'N/A', 'Outliers <60': 'N/A',
                'CV (%)': 'N/A', 'ARV': 'N/A'
            }
            continue

        min_sbp = sbp.min()
        max_sbp = sbp.max()
    
        # Split outliers
        outliers_high = (sbp > 150).sum() 
        outliers_low = (sbp < 60).sum()
        outliers_total = outliers_high + outliers_low

        mean_sbp = sbp.mean()
        std_sbp = sbp.std()
        cv = (std_sbp / mean_sbp * 100) if mean_sbp != 0 else np.nan

        if len(sbp) > 1:
            arv = np.mean(np.abs(np.diff(sbp)))
        else:
            arv = np.nan

        stats[phase] = {
            'Min SBP': round(min_sbp, 1),
            'Max SBP': round(max_sbp, 1),
            'Outliers Total': int(outliers_total),
            'Outliers > 150': int(outliers_high),
            'Outliers <60': int(outliers_low),
            'CV (%)': round(cv, 2) if not np.isnan(cv) else 'N/A',
            'ARV': round(arv, 2) if not np.isnan(arv) else 'N/A'
        }
    return stats

def plot_period_averages_and_shading(ax, df_phase):
    """
    Finds contiguous blocks of Day/Night, shades the night regions, and plots 
    the separate Day/Night average SBP and DBP as horizontal dashed lines.
    """
    # Create a safe copy and strictly boolean 'is_night' column
    df_phase = df_phase.copy()
    df_phase['is_night'] = df_phase['Day_Night'].astype(str).str.strip().str.lower() == 'night'
    
    # Calculate global means for the phase
    day_sbp = df_phase[~df_phase['is_night']]['SBP'].mean()
    day_dbp = df_phase[~df_phase['is_night']]['DBP'].mean()
    night_sbp = df_phase[df_phase['is_night']]['SBP'].mean()
    night_dbp = df_phase[df_phase['is_night']]['DBP'].mean()

    current_state = None
    start_time = None

    for idx, row in df_phase.iterrows():
        state = 'night' if row['is_night'] else 'day'
        
        if current_state is None:
            current_state = state
            start_time = row['Continuous_Time']
        elif state != current_state:
            # We hit a transition boundary, cap the end time
            end_time = row['Continuous_Time']
            
            # Draw for the previous block
            if current_state == 'night':
                ax.axvspan(start_time, end_time, color='darkgrey', alpha=0.3)
                if pd.notna(night_sbp): ax.hlines(night_sbp, start_time, end_time, color='#d62728', linestyle='--', alpha=0.6, linewidth=1.5)
                if pd.notna(night_dbp): ax.hlines(night_dbp, start_time, end_time, color='#1f77b4', linestyle='--', alpha=0.6, linewidth=1.5)
            else: # Day
                if pd.notna(day_sbp): ax.hlines(day_sbp, start_time, end_time, color='#d62728', linestyle='--', alpha=0.6, linewidth=1.5)
                if pd.notna(day_dbp): ax.hlines(day_dbp, start_time, end_time, color='#1f77b4', linestyle='--', alpha=0.6, linewidth=1.5)
            
            # Reset for the new block
            current_state = state
            start_time = row['Continuous_Time']

    # Catch the final trailing block when the loop ends
    if current_state is not None and start_time is not None:
        end_time = df_phase['Continuous_Time'].iloc[-1]
        if current_state == 'night':
            ax.axvspan(start_time, end_time, color='darkgrey', alpha=0.3)
            if pd.notna(night_sbp): ax.hlines(night_sbp, start_time, end_time, color='#d62728', linestyle='--', alpha=0.6, linewidth=1.5)
            if pd.notna(night_dbp): ax.hlines(night_dbp, start_time, end_time, color='#1f77b4', linestyle='--', alpha=0.6, linewidth=1.5)
        else: # Day
            if pd.notna(day_sbp): ax.hlines(day_sbp, start_time, end_time, color='#d62728', linestyle='--', alpha=0.6, linewidth=1.5)
            if pd.notna(day_dbp): ax.hlines(day_dbp, start_time, end_time, color='#1f77b4', linestyle='--', alpha=0.6, linewidth=1.5)

def plot_participant(df_participant, stats_dict, participant_id, reliability_dict):
    """
    Generates the stacked plots and the side statistics text.
    NOW ACCEPTS a reliability_dict to dynamically update graph titles.
    """
    fig = plt.figure(figsize=(15, 9))
    gs = gridspec.GridSpec(2, 2, width_ratios=[3.5, 1])

    ax_pre = fig.add_subplot(gs[0, 0])
    ax_post = fig.add_subplot(gs[1, 0])
    ax_stats = fig.add_subplot(gs[:, 1])

    ax_stats.axis('off')

    def format_axis(ax, title):
        ax.set_ylim(20, 200)
        ax.set_title(title)
        ax.set_ylabel('mmHg / BPM')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.tick_params(axis='x', labelbottom=True) 
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    def draw_traces(ax, df_phase):
        """Helper to draw all the new complex layering cleanly."""
        plot_period_averages_and_shading(ax, df_phase)
        
        # We create temporary 'valid' dataframes right before plotting.
        # This connects the gaps in the lines without altering the original df_phase.
        
        # 1. Pulse Pressure Area Shading and Stems (Require BOTH SBP and DBP to exist)
        valid_bp = df_phase.dropna(subset=['SBP', 'DBP', 'Continuous_Time'])
        ax.fill_between(valid_bp['Continuous_Time'], valid_bp['DBP'], valid_bp['SBP'], color='lightgrey', alpha=0.4, label='_nolegend_')
        ax.vlines(valid_bp['Continuous_Time'], valid_bp['DBP'], valid_bp['SBP'], color='gray', alpha=0.5, linestyle='-', linewidth=1.5)

        # 2. SBP Main Plot
        valid_sbp = df_phase.dropna(subset=['SBP', 'Continuous_Time'])
        ax.plot(valid_sbp['Continuous_Time'], valid_sbp['SBP'], marker='^', linestyle='-', color='#d62728', label='SBP', markersize=6)
        
        # 3. DBP Main Plot
        valid_dbp = df_phase.dropna(subset=['DBP', 'Continuous_Time'])
        ax.plot(valid_dbp['Continuous_Time'], valid_dbp['DBP'], marker='v', linestyle='-', color='#1f77b4', label='DBP', markersize=6)
        
        # 4. BPM Main Plot
        valid_bpm = df_phase.dropna(subset=['BPM', 'Continuous_Time'])
        ax.plot(valid_bpm['Continuous_Time'], valid_bpm['BPM'], marker='o', linestyle='-', color='#2ca02c', alpha=0.7, label='HR (BPM)', markersize=5)

    # --- Baseline PLOT ---
    pre_df = df_participant[df_participant['Intervention'] == 'Pre'].copy()
    if pre_df.empty or pre_df['SBP'].dropna().empty:
        ax_pre.text(0.5, 0.5, 'No Baseline Data Available', ha='center', va='center', fontsize=14)
        ax_pre.set_yticks([])
    else:
        draw_traces(ax_pre, pre_df)
        # INJECT THE RELIABILITY SCORE INTO THE TITLE
        format_axis(ax_pre, f'Baseline Vitals (Reliability: {reliability_dict["Pre"]}%)')
        ax_pre.set_xlabel('Time') 
        ax_pre.legend(loc='upper right', bbox_to_anchor=(1.0, 1.05))

    # --- POST-Intervention PLOT ---
    post_df = df_participant[df_participant['Intervention'] == 'Post'].copy()
    if post_df.empty or post_df['SBP'].dropna().empty:
        ax_post.text(0.5, 0.5, 'No Post-Intervention Data Available', ha='center', va='center', fontsize=14)
        ax_post.set_yticks([])
    else:
        draw_traces(ax_post, post_df)
        # INJECT THE RELIABILITY SCORE INTO THE TITLE
        format_axis(ax_post, f'Post-Intervention Vitals (Reliability: {reliability_dict["Post"]}%)')
        ax_post.set_xlabel('Time')
        ax_post.legend(loc='upper right', bbox_to_anchor=(1.0, 1.05))
        

    # --- STATISTICS PANEL ---
    stat_text = f"Participant: {participant_id}\n\n"
    stat_text += "-"*30 + "\n"
    
    metrics = ['Min SBP', 'Max SBP', 'Outliers Total', 'Outliers > 150', 'Outliers <60', 'CV (%)', 'ARV']
    for metric in metrics:
        pre_val = stats_dict['Pre'][metric]
        post_val = stats_dict['Post'][metric]
        stat_text += f"{metric}:\n  {pre_val} -> {post_val}\n\n"

    ax_stats.text(0.05, 0.95, stat_text, va='top', ha='left', fontsize=11,
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray', boxstyle='round,pad=1'))

    plt.tight_layout()

    plt.savefig(f"/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Participant Plots March 2026/{participant_id}_BP_Plot.png", dpi=300)
    #plt.show()
    plt.close(fig)

def main():
    # 1. Load Original Data
    df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/All Participant Raw Data Long Form.csv')
    df = preprocess_data(df)
    
    # 2. Load NEW Reliability Scores (Make sure this path is correct for your computer!)
    rel_df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Reliability Scores March 2026.csv')
    
    participants = df['Participant'].unique()
    all_stats_list = []

    for p_id in participants:
        # A. Filter Main Data
        p_df = df[df['Participant'] == p_id].copy()
        p_df.sort_values('Continuous_Time', inplace=True)
        
        # B. Filter Reliability Data for this specific participant
        p_rel = rel_df[rel_df['Participant'] == p_id]
        
        # Create our "cheat sheet" dictionary with N/A defaults just in case
        reliability_dict = {'Pre': 'N/A', 'Post': 'N/A'}
        
        # Populate the dictionary with their actual scores
        for _, rel_row in p_rel.iterrows():
            if rel_row['Intervention'] == 'Pre':
                reliability_dict['Pre'] = rel_row['Reliability %']
            elif rel_row['Intervention'] == 'Post':
                reliability_dict['Post'] = rel_row['Reliability %']

        # C. Calculate Stats and Plot
        stats_dict = calculate_statistics(p_df)
        
        # Pass the new reliability_dict right into our plotting function!
        plot_participant(p_df, stats_dict, p_id, reliability_dict)
        
        # D. Save to output list
        row_data = {'Participant': p_id}
        for phase in ['Pre', 'Post']:
            for k, v in stats_dict[phase].items():
                row_data[f"{phase}_{k}"] = v
        all_stats_list.append(row_data)

    # 3. Export Final CSV
    stats_df = pd.DataFrame(all_stats_list)
    stats_df.to_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Participant Plots March 2026/New_Participant_Statistics.csv', index=False)
    print("Processing complete. Saved Participant_Statistics.csv and updated plots.")

if __name__ == "__main__":
    main()


'''
import pandas as pd 

df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/All Participant Raw Data Long Form.csv')
participants = df["Participant"].to_list()
participants = list(set(participants))
participants.sort()
print(participants)
'''


'''#The following script will look for missing data between files and list it out 
import pandas as pd

# Load the datasets
df1 = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/Summary.csv')
df2 = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/All Participant Raw Data.csv')

# Count unique occurrences of the combination in File 1
# We group by both columns and count the size of each group
counts1 = df1.groupby(["Participant", "Pre or Post"]).size().reset_index(name='count_file1')
print(counts1)
id_1 = counts1["Participant"].to_list()
intervention_1 = counts1["Pre or Post"].to_list()

tuples_1 = []
for x in range(0, len(id_1)):
    one = id_1[x]
    two = intervention_1[x]
    tuples_1.append((one, two))


# Count unique occurrences of the combination in File 2
counts2 = df2.groupby(["Participant", "Intervention"]).size().reset_index(name='count_file2')
print(counts1)
id_2 = counts2["Participant"].to_list()
intervention_2 = counts2["Intervention"].to_list()

tuples_2 = []
for x in range(0, len(id_2)):
    one = id_2[x]
    two = intervention_2[x]
    tuples_2.append((one, two))


for x in range (0, len(tuples_1)):
    tuple = tuples_1[x]
    list_checker = []
    for y in tuples_2:
        if tuple == y: 
            list_checker.append(y)
        else: 
            continue 
    if len(list_checker) == 0: 
        print(f"Could not find match for {tuple} from Summary File in Long Format File")

for x in range (0, len(tuples_2)):
    tuple = tuples_2[x]
    list_checker = []
    for y in tuples_1:
        if tuple == y: 
            list_checker.append(y)
        else: 
            continue 
    if len(list_checker) == 0: 
        print(f"Could not find match for {tuple} from Long Format File in Summary File")

print("Differences:")
differences = set(tuples_2) ^ set(tuples_1)
print(differences)
print()
print()

print(tuples_1)
print()
print(tuples_2)'''




