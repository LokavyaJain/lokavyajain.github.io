#This script produces raincloud plots using matplotlib


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl

# ==========================================
# Set "Ugly Publication" Style Defaults
# ==========================================
#mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.linewidth'] = 1.5
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['xtick.major.width'] = 1.5
mpl.rcParams['ytick.major.width'] = 1.5
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['ytick.major.size'] = 5

def plot_custom_raincloud(pre_data, post_data, p_value="N/A", d_value="N/A", ylabel="Amplitude (mmHg)", title=""):
    """
    Plots a mirrored academic raincloud plot with half-violins, BOX PLOTS, and connected points.
    Both sides are fully shaded.
    """
    pre_data = np.array(pre_data)
    post_data = np.array(post_data)

    fig, ax = plt.subplots(figsize=(3.25, 5))

    # --- POSITIONING VARIABLES ---
    pos_pre_dots = -0.1
    pos_post_dots = 0.1
    
    pos_pre_box = -0.35
    pos_post_box = 0.35
    
    pos_pre_violin = -0.6
    pos_post_violin = 0.6

    # 1. CENTER: Plot individual points and connecting lines
    for i in range(len(pre_data)):
        ax.plot([pos_pre_dots, pos_post_dots], [pre_data[i], post_data[i]], 
                color='gray', linestyle='--', linewidth=0.75, zorder=1, alpha = 0.5)
    
    # Scatter points
    ax.scatter(np.repeat(pos_pre_dots, len(pre_data)), pre_data, color='black', edgecolor='black', s=25, zorder=2)
    ax.scatter(np.repeat(pos_post_dots, len(post_data)), post_data, color='black', edgecolor='black', linewidth=1, s=25, zorder=2)

    # 2. MIDDLE LAYER: Box plots instead of Bar graphs
    box_width = 0.20
    medianprops = dict(color='black', linewidth=2)
    whiskerprops = dict(color='black', linewidth=1.5, linestyle='-')
    capprops = dict(color='black', linewidth=1.5)

    # Baseline Box - NOW SHADED LIGHTGRAY
    ax.boxplot(pre_data, positions=[pos_pre_box], widths=box_width, patch_artist=True,
               boxprops=dict(facecolor='lightgray', color='black', linewidth=1.5), 
               medianprops=medianprops, whiskerprops=whiskerprops, capprops=capprops, zorder=3, showfliers=False)
               
    # PostStim Box
    ax.boxplot(post_data, positions=[pos_post_box], widths=box_width, patch_artist=True,
               boxprops=dict(facecolor='lightgray', color='black', linewidth=1.5), 
               medianprops=medianprops, whiskerprops=whiskerprops, capprops=capprops, zorder=3, showfliers=False)

    # 3. OUTER LAYER: Half-Violin plots with harsh borders
    # Baseline Violin - NOW SHADED LIGHTGRAY
    v_pre = ax.violinplot(pre_data, positions=[pos_pre_violin], showmeans=False, showextrema=False)
    for b in v_pre['bodies']:
        b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths()[0].vertices[:, 0], -np.inf, pos_pre_violin)
        b.set_facecolor('lightgray')
        b.set_edgecolor('black')
        b.set_linewidth(1.5)
        b.set_alpha(1)

    # PostStim Violin
    v_post = ax.violinplot(post_data, positions=[pos_post_violin], showmeans=False, showextrema=False)
    for b in v_post['bodies']:
        b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths()[0].vertices[:, 0], pos_post_violin, np.inf)
        b.set_facecolor('lightgray')
        b.set_edgecolor('black')
        b.set_linewidth(1.5)
        b.set_alpha(1)

    # --- ANNOTATIONS & FORMATTING ---
    max_y = max(np.max(pre_data), np.max(post_data))
    min_y = min(np.min(pre_data), np.min(post_data))
    
    if p_value != "N/A" or d_value != "N/A":
        ax.text(0, max_y * 1.05, f'p = {p_value}, d = {d_value}', 
                ha='center', va='bottom', fontsize=12)

    ax.set_xticks([pos_pre_box, pos_post_box])
    ax.set_xticklabels(['Baseline', 'PostStim'], fontweight='bold')
    ax.set_ylabel("", fontweight='bold')
    
    if title:
        ax.set_title(title, fontweight='bold', pad=15)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlim(-1, 1)
    #ax.set_ylim(0, 28)

    #custom_y_ticks = [5, 10, 15, 20, 25]
    #ax.set_yticks(custom_y_ticks)

    ax.set_ylim(bottom=min_y * 0.9, top=max_y * 1.15)
    
    plt.tight_layout()

    plt.savefig(f'/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/COSINOR/Cosinor Plots/{ylabel} Violin.png', dpi = 200)



def process_csv_and_plot(csv_path, metric_col, p_value="N/A", d_value="N/A", ylabel=None):
    df = pd.read_csv(csv_path)

    participant_IDs = ["ISRT01", "ISRT02", "ISRT04", "ISRT05", "ISRT06", "ISRT07", "ISRT16", "ISRT20", "DOD08", "DOD17"]

    df = df[df['Participant'].isin(participant_IDs)]

    df_pre = df[df['Pre or Post'] == 'Pre'].set_index('Participant')
    df_post = df[df['Pre or Post'] == 'Post'].set_index('Participant')
    
    paired_df = df_pre.join(df_post, lsuffix='_pre', rsuffix='_post', how='inner')
    paired_df = paired_df.dropna(subset=[f'{metric_col}_pre', f'{metric_col}_post'])
    
    pre_data = paired_df[f'{metric_col}_pre'].values
    post_data = paired_df[f'{metric_col}_post'].values
    
    if len(pre_data) == 0:
        raise ValueError(f"No valid paired data found for '{metric_col}'.")
        
    if ylabel is None:
        ylabel = metric_col
        
    plot_custom_raincloud(
        pre_data=pre_data, 
        post_data=post_data, 
        p_value=p_value, 
        d_value=d_value,
        ylabel=ylabel,
        title=f"Baseline vs PostStim: {metric_col}"
    )

# ==========================================
# Example usage:
# ==========================================
if __name__ == "__main__":
    file_path = '/Users/lokavyajain/Desktop/Lab_Volunteering/24h Blood Pressure/24HourABPM Summary for Shane.csv'

    process_csv_and_plot(
        csv_path=file_path, 
        metric_col='Mean_DBP', 
        p_value="0.021",
        d_value="0.46",
        ylabel="Amplitude (mmHg)"
    )

