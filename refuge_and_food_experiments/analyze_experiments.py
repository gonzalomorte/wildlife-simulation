"""
Analysis script for wildlife simulation experiments.

Analyzes success rates and generates visualizations for:
- Experiment Set A: Refuge capacity effect
- Experiment Set B: Food ratio effect

For each parameter value, generates evolution plots showing all 5 replicates.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import glob
import argparse


def plot_value_evolution(df, param_col, param_value, set_name, param_name, fixed_param_name=None, fixed_param_value=None):
    """
    Plot time series evolution for one parameter value.
    - Mean boids_alive and predators_alive across replicates (thick lines)
    - Individual replicates as light lines (if >1)
    - Uses two subplots to avoid overlap issues
    """
    value_data = df[df[param_col] == param_value].copy()
    run_ids = sorted(value_data['run_id'].unique())

    # Get all unique timestamps across all runs
    all_timestamps = sorted(value_data['timestamp_sec'].unique())
    
    # For each run, forward-fill missing timestamps with last known value
    aligned_data = []
    for run_id in run_ids:
        run_data = value_data[value_data['run_id'] == run_id].sort_values('timestamp_sec')
        
        # Create a full timestamp series for this run
        full_series = pd.DataFrame({'timestamp_sec': all_timestamps})
        full_series = full_series.merge(run_data[['timestamp_sec', 'boids_alive', 'predators_alive']], 
                                        on='timestamp_sec', how='left')
        
        # Forward fill: propagate last known values (when sim ends, values stay at final state)
        full_series['boids_alive'] = full_series['boids_alive'].fillna(method='ffill')
        full_series['predators_alive'] = full_series['predators_alive'].fillna(method='ffill')
        
        # If there are still NaNs at the beginning, fill with 0
        full_series = full_series.fillna(0)
        
        full_series['run_id'] = run_id
        aligned_data.append(full_series)
    
    # Concatenate all aligned runs
    aligned_df = pd.concat(aligned_data, ignore_index=True)
    
    # Now calculate mean across runs for each timestamp
    mean_series = (
        aligned_df.groupby('timestamp_sec')[['boids_alive', 'predators_alive']]
        .mean()
        .reset_index()
        .sort_values('timestamp_sec')
    )

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    title_str = f'Set {set_name}: {param_name} = {param_value}'
    if fixed_param_name and fixed_param_value is not None:
        title_str += f', {fixed_param_name} = {fixed_param_value}'
    fig.suptitle(
        title_str,
        fontsize=14,
        fontweight='bold'
    )

    # Boids subplot (mean only)
    ax = axes[0]
    ax.plot(
        mean_series['timestamp_sec'],
        mean_series['boids_alive'],
        color='#1f77b4', linewidth=2.5, marker='o', label='Boids (mean)'
    )
    ax.set_ylabel('Boids alive', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(loc='best')

    # Predators subplot (mean only)
    ax = axes[1]
    ax.plot(
        mean_series['timestamp_sec'],
        mean_series['predators_alive'],
        color='#ff7f0e', linewidth=2.5, marker='s', label='Predators (mean)'
    )
    ax.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Predators alive', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(loc='best')

    plt.tight_layout()

    os.makedirs('simulation_logs/evolution_plots', exist_ok=True)
    output_file = f'simulation_logs/evolution_plots/set_{set_name}_{param_col}_{param_value}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def plot_mean_by_param(final_states, param_col, set_name, param_name, fixed_param_name=None, fixed_param_value=None):
    """Plot mean final boids/predators per parameter value."""
    grouped = final_states.groupby(param_col)[['boids_alive', 'predators_alive']].mean().reset_index()
    grouped = grouped.sort_values(param_col)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(grouped[param_col], grouped['boids_alive'], marker='o', color='#1f77b4', linewidth=2.5, label='Boids (final mean)')
    ax.plot(grouped[param_col], grouped['predators_alive'], marker='s', linestyle='--', color='#ff7f0e', linewidth=2.5, label='Predators (final mean)')

    ax.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax.set_ylabel('Final alive count', fontsize=12, fontweight='bold')
    title_str = f'Set {set_name}: Final populations (mean over replicates)'
    if fixed_param_name and fixed_param_value is not None:
        title_str += f' | {fixed_param_name} = {fixed_param_value}'
    ax.set_title(title_str, fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend()

    plt.tight_layout()
    os.makedirs('simulation_logs/evolution_plots', exist_ok=True)
    output_file = f'simulation_logs/evolution_plots/set_{set_name}_{param_col}_final_means.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def analyze_experiment(csv_pattern, param_name, param_col, set_name):
    """
    Analyze a single experiment set from one or more CSV files.
    
    Args:
        csv_pattern: Glob pattern or file path for CSV files
        param_name: Human-readable parameter name
        param_col: Column name for the varied parameter
        set_name: Set identifier (A or B)
    """
    # Find all matching CSV files
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"Error: No files found matching pattern: {csv_pattern}")
        return
    
    print(f"\n{'='*70}")
    print(f"Analyzing Set {set_name}: {param_name}")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV file(s):")
    for f in csv_files:
        print(f"  - {f}")
    print()
    
    # Load and concatenate all CSV files
    dfs = []
    for csv_file in csv_files:
        df_temp = pd.read_csv(csv_file)
        dfs.append(df_temp)
    
    df = pd.concat(dfs, ignore_index=True)
    
    print(f"Total data points loaded: {len(df)}")
    print(f"Unique run_ids: {df['run_id'].nunique()}")
    print()
    
    # Get final state for each run
    final_states = df.groupby('run_id').last().reset_index()
    
    # Calculate success (predators extinct AND boids alive)
    final_states['success'] = (
        (final_states['predators_alive'] == 0) & 
        (final_states['boids_alive'] > 0)
    )
    
    # Calculate failure (boids extinct)
    final_states['failure'] = (final_states['boids_alive'] == 0)
    
    # Group by parameter value
    results = final_states.groupby(param_col).agg({
        'success': ['sum', 'mean', 'count'],
        'failure': 'sum',
        'boids_alive': ['mean', 'std'],
        'predators_alive': ['mean', 'std'],
        'timestamp_sec': ['mean', 'std']
    }).round(3)
    
    print("Results by parameter value:")
    print(results)
    print()
    
    # Success rate summary
    print(f"Overall Statistics:")
    print(f"  Total runs: {len(final_states)}")
    print(f"  Success (predators starved, boids survived): {final_states['success'].sum()} ({final_states['success'].mean()*100:.1f}%)")
    print(f"  Failure (boids extinct): {final_states['failure'].sum()} ({final_states['failure'].mean()*100:.1f}%)")
    print(f"  Inconclusive (both survived): {(~final_states['success'] & ~final_states['failure']).sum()}")
    print()
    
    # Determine fixed parameter info
    fixed_param_name = None
    fixed_param_value = None
    if param_col == 'refuge_capacity':
        fixed_param_name = 'Food Ratio'
        fixed_param_value = df['food_ratio'].iloc[0]
    elif param_col == 'food_ratio':
        fixed_param_name = 'Refuge Capacity'
        fixed_param_value = df['refuge_capacity'].iloc[0]
    
    # Generate evolution plots for each parameter value
    print(f"Generating evolution plots for each {param_name} value...")
    param_values = sorted(df[param_col].unique())
    
    for param_value in param_values:
        output_file = plot_value_evolution(df, param_col, param_value, set_name, param_name, fixed_param_name, fixed_param_value)
        print(f"  ✓ {param_name} = {param_value}: {output_file}")
    
    # Plot mean final populations per parameter value
    plot_mean_by_param(final_states, param_col, set_name, param_name, fixed_param_name, fixed_param_value)
    print(f"  ✓ Final means plot saved for {param_name}")
    print()
    
    # Generate summary plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    title_str = f'Set {set_name}: {param_name} Effect on Boid Survival'
    if fixed_param_name and fixed_param_value is not None:
        title_str += f' | {fixed_param_name} = {fixed_param_value}'
    fig.suptitle(title_str, fontsize=16, fontweight='bold')
    
    # Plot 1: Success rate
    success_rate = final_states.groupby(param_col)['success'].agg(['mean', 'std']).reset_index()
    axes[0, 0].bar(success_rate[param_col], success_rate['mean'], 
                   yerr=success_rate['std'], capsize=5, alpha=0.7, color='green')
    axes[0, 0].set_xlabel(param_name)
    axes[0, 0].set_ylabel('Success Rate')
    axes[0, 0].set_title('Success Rate (Boids Survive Until Predators Starve)')
    axes[0, 0].set_ylim([0, 1.0])
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Final boid count
    axes[0, 1].boxplot([final_states[final_states[param_col] == val]['boids_alive'] 
                        for val in sorted(final_states[param_col].unique())],
                       labels=sorted(final_states[param_col].unique()))
    axes[0, 1].set_xlabel(param_name)
    axes[0, 1].set_ylabel('Final Boid Count')
    axes[0, 1].set_title('Final Boid Count Distribution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Time to extinction
    axes[1, 0].boxplot([final_states[final_states[param_col] == val]['timestamp_sec'] 
                        for val in sorted(final_states[param_col].unique())],
                       labels=sorted(final_states[param_col].unique()))
    axes[1, 0].set_xlabel(param_name)
    axes[1, 0].set_ylabel('Simulation Duration (seconds)')
    axes[1, 0].set_title('Time Until Extinction')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Outcome distribution
    param_values = sorted(final_states[param_col].unique())
    success_counts = [final_states[(final_states[param_col] == val) & final_states['success']].shape[0] 
                     for val in param_values]
    failure_counts = [final_states[(final_states[param_col] == val) & final_states['failure']].shape[0] 
                     for val in param_values]
    inconclusive_counts = [final_states[(final_states[param_col] == val) & ~final_states['success'] & ~final_states['failure']].shape[0] 
                          for val in param_values]
    
    x = range(len(param_values))
    width = 0.6
    axes[1, 1].bar(x, success_counts, width, label='Success', color='green', alpha=0.7)
    axes[1, 1].bar(x, failure_counts, width, bottom=success_counts, label='Failure', color='red', alpha=0.7)
    axes[1, 1].bar(x, inconclusive_counts, width, 
                   bottom=[s+f for s, f in zip(success_counts, failure_counts)], 
                   label='Inconclusive', color='gray', alpha=0.7)
    axes[1, 1].set_xlabel(param_name)
    axes[1, 1].set_ylabel('Number of Runs')
    axes[1, 1].set_title('Outcome Distribution')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels([str(v) for v in param_values])
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    base_name = os.path.basename(csv_files[0]).replace('.csv', '')
    output_file = f'simulation_logs/{base_name}_summary.png'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Summary plot saved: {output_file}")
    
    plt.close()


def main():
    """Analyze experiment sets with command-line arguments."""
    
    parser = argparse.ArgumentParser(description='Analyze wildlife simulation experiments')
    parser.add_argument(
        '--set',
        choices=['A', 'B', 'both'],
        default=None,
        help='Which experiment set to analyze: A (refuge capacity), B (food ratio), or both'
    )
    parser.add_argument(
        '--file',
        type=str,
        default=None,
        help='Analyze a specific CSV file (e.g., simulation_logs/experiments_refuge_capacity_20260120_104014.csv)'
    )
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("WILDLIFE SIMULATION EXPERIMENT ANALYSIS")
    print("="*70)
    
    # If --file is provided, analyze that specific file
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        # Determine set type and param from filename
        if 'refuge_capacity' in args.file:
            analyze_experiment(
                args.file,
                'Refuge Capacity',
                'refuge_capacity',
                'A'
            )
        elif 'food_ratio' in args.file:
            analyze_experiment(
                args.file,
                'Food Ratio',
                'food_ratio',
                'B'
            )
        else:
            print("Error: Could not determine set type from filename")
            return
    else:
        # If --set is not provided, default to 'both'
        set_arg = args.set if args.set else 'both'
        
        if set_arg in ['A', 'both']:
            # Analyze Set A: Refuge Capacity (finds all timestamped files)
            analyze_experiment(
                'simulation_logs/experiments_refuge_capacity*.csv',
                'Refuge Capacity',
                'refuge_capacity',
                'A'
            )
        
        if set_arg in ['B', 'both']:
            # Analyze Set B: Food Ratio (finds all timestamped files)
            analyze_experiment(
                'simulation_logs/experiments_food_ratio*.csv',
                'Food Ratio',
                'food_ratio',
                'B'
            )
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nEvolution plots saved in: simulation_logs/evolution_plots/")
    print(f"Summary plots saved in: simulation_logs/")


if __name__ == "__main__":
    main()
