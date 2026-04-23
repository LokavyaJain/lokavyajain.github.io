'''

import matplotlib.pyplot as plt
import numpy as np

# Data
conditions = ['Baseline', 'Post-Stimulation']
means = [9.3, 13.2]
std_devs = [3.5, 4.4]

# Create plot (narrower overall figure width to match classic style)
fig, ax = plt.subplots(figsize=(4, 4))

# Plot bars with classic styling (black, narrower width, thick error bars)
bars = ax.bar(conditions, means, yerr=std_devs, width=0.5, color='black', edgecolor='black',
              error_kw=dict(lw=2, capsize=6, capthick=2))

# Add labels and title
ax.set_ylabel('Acrophase Time (Hours)', fontsize=12, fontweight='bold')
# Classic figures often don't have titles, or have very simple ones. We'll keep it simple.
# ax.set_title('Shift in SBP Acrophase', fontsize=12, fontweight='bold')
ax.set_ylim(0, 20)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Make the remaining bottom and left spines thicker to mimic older software
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

# Make tick marks thicker and face outward (a very classic look)
ax.tick_params(axis='both', which='major', width=1.5, length=5, direction='out')

# Remove background grid
ax.grid(False)

# Add statistical significance annotation
x1, x2 = 0, 1
y_max = max(means[0] + std_devs[0], means[1] + std_devs[1]) + 1
ax.plot([x1, x1, x2, x2], [y_max, y_max+0.5, y_max+0.5, y_max], lw=1.5, color='black')
ax.text((x1+x2)*.5, y_max + 0.5, '* p = 0.013', ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()


'''




import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

# 1. Create Made-up Dataset (n=10) mimicking Daytime AD events
# Baseline: Higher frequency, PostStim: Lower frequency
np.random.seed(42)
baseline = np.array([18, 28, 45, 10, 2, 22, 16, 19, 1, 0])
post_stim = np.array([7, 8, 17, 6, 0, 8, 2, 1, 0, 0])
data = [baseline, post_stim]

fig, ax = plt.subplots(figsize=(7, 6))

# Styling variables
colors = ['#d3d3d3', '#d3d3d3'] # Light grey as seen in the manuscript
positions = [1, 2]
jitter_val = 0.08

for i, (d, pos) in enumerate(zip(data, positions)):
    # --- A. Half-Violin (Density) ---
    kde = gaussian_kde(d)
    y_range = np.linspace(d.min() - 2, d.max() + 2, 100)
    density = kde(y_range)
    density = density / density.max() * 0.3  # Scale for width
    
    # Mirroring: Baseline density to the left, PostStim to the right
    if i == 0:
        ax.fill_betweenx(y_range, pos - 0.4, pos - 0.4 - density, color=colors[i], alpha=0.6)
    else:
        ax.fill_betweenx(y_range, pos + 0.4, pos + 0.4 + density, color=colors[i], alpha=0.6)

    # --- B. Boxplot (Central) ---
    bp = ax.boxplot(d, positions=[pos], widths=0.15, patch_artist=True,
                    showfliers=False, zorder=3)
    for patch in bp['boxes']:
        patch.set(facecolor=colors[i], alpha=0.8, linewidth=1.5)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)

# --- C. Raw Data Points & Connection Lines ---
# We calculate jitter once to use for both ends of the line
jitter = np.random.uniform(-jitter_val, jitter_val, len(baseline))
x_base = np.full(len(baseline), 1) + 0.2 + jitter
x_post = np.full(len(post_stim), 2) - 0.2 + jitter

for j in range(len(baseline)):
    # Dashed lines connecting pairs
    ax.plot([x_base[j], x_post[j]], [baseline[j], post_stim[j]], 
            color='gray', linestyle='--', linewidth=1, alpha=0.5, zorder=1)
    # Scatter points
    ax.scatter(x_base[j], baseline[j], color='black', s=40, zorder=4)
    ax.scatter(x_post[j], post_stim[j], color='black', s=40, zorder=4)

# --- D. Significance Bracket ---
x1, x2 = 1, 2
y_max = max(baseline.max(), post_stim.max()) + 5
ax.plot([x1, x1, x2, x2], [y_max, y_max+2, y_max+2, y_max], color='black', lw=1.5)
ax.text((x1+x2)/2, y_max+2.5, 'p = 0.016, g = -0.93', ha='center', va='bottom', fontsize=11)

# --- E. "Classic Academic" Skinning ---
ax.set_xticks(positions)
ax.set_xticklabels(['Baseline', 'PostStim'], fontsize=12, fontweight='bold')
ax.set_ylabel('Daytime AD events (count)', fontsize=12, fontweight='bold')
ax.set_ylim(-2, 60)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(direction='out', length=6, width=1.5)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

plt.tight_layout()
plt.show()
