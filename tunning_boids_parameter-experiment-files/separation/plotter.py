import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the dataset
# This file includes data up to sep=3.0 and durations up to 120 seconds
file_name = 'experiments_sep_new.csv'
df = pd.read_csv(file_name)

# 2. Data Preprocessing
# Truncate timestamp_sec to integers to group data points by second.
# This prevents visual "jumps" in the mean at the end of the simulation.
df['time_seconds'] = df['timestamp_sec'].astype(int)

# 3. Define Reliable Metrics
# We are excluding distance and velocity metrics as requested.
# We include predator metrics to monitor starvation.
reliable_metrics = ['boids_alive', 'boids_eaten', 'boids_in_refuge', 'predators_alive']

# Calculate the mean for these metrics grouped by 'sep' and time
df_avg = df.groupby(['sep', 'time_seconds'])[reliable_metrics].mean().reset_index()

# 4. Global Styling
sns.set_theme(style="whitegrid")

# Function to create and save faceted plots
def create_faceted_plot(data, y_var, title, filename, color, y_limit=None):
    g = sns.relplot(
        data=data,
        x="time_seconds", y=y_var,
        col="sep", col_wrap=4,
        kind="line", height=3, aspect=1.2, color=color, linewidth=2
    )
    g.set_axis_labels("Time (seconds)", y_var.replace('_', ' ').title())
    g.set_titles("sep = {col_name}")
    g.set(xlim=(0, 120))
    if y_limit:
        g.set(ylim=y_limit)
    
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(title)
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    return g

# 5. Generate the individual analysis plots
# --- Plot A: Boid Survival ---
create_faceted_plot(df_avg, 'boids_alive', 'Boid Survival Rate Over Time', 
                    'analysis_boids_alive.png', 'royalblue', y_limit=(0, 21))

# --- Plot B: Predator Survival (Starvation Check) ---
# This shows if predators die over time (3 = all alive, <3 = some starved)
create_faceted_plot(df_avg, 'predators_alive', 'Predator Survival Rate (Starvation Monitoring)', 
                    'analysis_predators_alive.png', 'darkorange', y_limit=(0, 3.5))

# --- Plot C: Cumulative Predation ---
create_faceted_plot(df_avg, 'boids_eaten', 'Cumulative Boids Eaten', 
                    'analysis_boids_eaten.png', 'crimson')

# --- Plot D: Refuge Usage ---
create_faceted_plot(df_avg, 'boids_in_refuge', 'Boids Inside Refuge Areas', 
                    'analysis_refuge_usage.png', 'forestgreen')

# 6. Show the interactive windows
plt.show()