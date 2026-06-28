import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the dataset
# Update the filename if your new file has a different name
file_name = 'experiments_coh.csv' 
df = pd.read_csv(file_name)

# 2. Data Preprocessing
# Truncate timestamp_sec to integers to group data points by second.
df['time_seconds'] = df['timestamp_sec'].astype(int)

# 3. Define Reliable Metrics
reliable_metrics = ['boids_alive', 'boids_eaten', 'boids_in_refuge', 'predators_alive']

# 4. Group by 'coh' instead of 'ali'
# We calculate the mean for each cohesion value at each second
df_avg = df.groupby(['coh', 'time_seconds'])[reliable_metrics].mean().reset_index()

# 5. Global Styling
sns.set_theme(style="whitegrid")

# Function to create and save faceted plots based on 'coh'
def create_faceted_plot(data, y_var, title, filename, color, y_limit=None):
    g = sns.relplot(
        data=data,
        x="time_seconds", y=y_var,
        col="coh",           # Facet by 'coh' variable
        col_wrap=4,          # Adjust columns in the grid
        kind="line", 
        height=3, 
        aspect=1.2, 
        color=color, 
        linewidth=2
    )
    g.set_axis_labels("Time (seconds)", y_var.replace('_', ' ').title())
    g.set_titles("coh = {col_name}") # Titles now show the cohesion value
    g.set(xlim=(0, 120))
    if y_limit:
        g.set(ylim=y_limit)
    
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle(title)
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")
    return g

# 6. Generate the individual analysis plots for 'coh'
# --- Plot A: Boid Survival ---
create_faceted_plot(df_avg, 'boids_alive', 'Boid Survival Rate Over Time (by Cohesion)', 
                    'analysis_coh_boids_alive.png', 'royalblue', y_limit=(0, 21))

# --- Plot B: Predator Survival ---
create_faceted_plot(df_avg, 'predators_alive', 'Predator Survival Rate (by Cohesion)', 
                    'analysis_coh_predators_alive.png', 'darkorange', y_limit=(0, 3.5))

# --- Plot C: Cumulative Predation ---
create_faceted_plot(df_avg, 'boids_eaten', 'Cumulative Boids Eaten (by Cohesion)', 
                    'analysis_coh_boids_eaten.png', 'crimson')

# --- Plot D: Refuge Usage ---
create_faceted_plot(df_avg, 'boids_in_refuge', 'Boids Inside Refuge Areas (by Cohesion)', 
                    'analysis_coh_refuge_usage.png', 'forestgreen')

# 7. Show the interactive windows
plt.show()