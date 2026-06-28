"""
Batch runner for wildlife simulation experiments.

Executes two experiment sets:
- Set A: Vary refuge capacity (4, 6, 8, 10) with fixed food ratio (0.7)
- Set B: Vary food ratio (0.3, 0.5, 0.7, 1.0, 1.5) with fixed refuge capacity (10)

Each configuration is run 5 times to account for randomness.
"""

import subprocess
import sys
import argparse
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

# Fixed experimental parameters
MAP_ID = 10
N_BOIDS = 10
N_PREDATORS = 1
REPLICATES = 15
NUM_WORKERS = 4  # Number of parallel processes (adjust based on your CPU cores)

# Experiment Set A: Refuge Capacity Effect
REFUGE_CAPACITIES = [2, 4, 6, 8, 10]
FIXED_FOOD_RATIO_A = 0.7

# Experiment Set B: Food Ratio Effect
FOOD_RATIOS = [0.1, 0.5, 1.0, 1.5, 2]
FIXED_REFUGE_CAPACITY_B = 6

def run_simulation(run_id, map_id, refuge_capacity, food_ratio, log_file):
    """Run a single simulation with specified parameters."""
    cmd = [
        sys.executable, "main.py",
        "-map", str(map_id),
        "--run-id", str(run_id),
        "--refuge-capacity", str(refuge_capacity),
        "--food-ratio", str(food_ratio),
        "--log-file", log_file,
        "--headless"
    ]
    
    print(f"  Running: run_id={run_id}, refuge_cap={refuge_capacity}, food_ratio={food_ratio}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    return True

def run_experiment_set(set_name, params_list, param_name, fixed_param, log_file_base):
    """Run one experiment set with specified parameters."""
    start_time = datetime.now()
    os.makedirs("simulation_logs", exist_ok=True)
    
    timestamp = start_time.strftime('%Y%m%d_%H%M%S')
    log_file = f"simulation_logs/{log_file_base}_{timestamp}.csv"
    
    print("="*70)
    print(f"EXPERIMENT SET {set_name}")
    print("="*70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nFixed parameters:")
    print(f"  Map: {MAP_ID}")
    print(f"  Boids: {N_BOIDS}")
    print(f"  Predators: {N_PREDATORS}")
    print(f"  {param_name}: {fixed_param}")
    print(f"  Replicates per value: {REPLICATES}")
    print(f"  Parallel workers: {NUM_WORKERS}")
    print()
    
    # Build tasks
    tasks = []
    run_id = 0
    
    for value in params_list:
        for rep in range(1, REPLICATES + 1):
            run_id += 1
            if set_name == "A":
                capacity, ratio = value, fixed_param
            else:
                capacity, ratio = fixed_param, value
            
            tasks.append({
                "run_id": run_id,
                "map_id": MAP_ID,
                "refuge_capacity": capacity,
                "food_ratio": ratio,
                "log_file": log_file,
                "set": set_name,
                "value": value
            })
    
    print(f"Total runs: {len(tasks)}")
    print(f"Running in parallel with {NUM_WORKERS} workers...")
    print("="*70 + "\n")
    
    # Execute
    completed = 0
    failed = 0
    
    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {
            executor.submit(
                run_simulation,
                task["run_id"],
                task["map_id"],
                task["refuge_capacity"],
                task["food_ratio"],
                task["log_file"]
            ): task for task in tasks
        }
        
        for future in as_completed(futures):
            task = futures[future]
            try:
                success = future.result()
                if success:
                    completed += 1
                    status = "✓"
                else:
                    failed += 1
                    status = "✗"
            except Exception as e:
                failed += 1
                status = "✗"
                print(f"  Run {task['run_id']}: ERROR - {e}")
            
            print(f"Set {set_name} - Value {task['value']}, Run {task['run_id']}: {status}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*70)
    print(f"SET {set_name} COMPLETE")
    print("="*70)
    print(f"Total runs: {len(tasks)}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Output file: {log_file}")
    print(f"Duration: {duration}")
    print(f"Average per run: {duration / len(tasks)}")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description='Run wildlife simulation experiments')
    parser.add_argument(
        '--set',
        choices=['A', 'B', 'both'],
        default='both',
        help='Which experiment set to run: A (refuge capacity), B (food ratio), or both'
    )
    args = parser.parse_args()
    
    if args.set in ['A', 'both']:
        run_experiment_set(
            "A",
            REFUGE_CAPACITIES,
            "Fixed food_ratio",
            FIXED_FOOD_RATIO_A,
            "experiments_refuge_capacity"
        )
    
    if args.set in ['B', 'both']:
        run_experiment_set(
            "B",
            FOOD_RATIOS,
            "Fixed refuge_capacity",
            FIXED_REFUGE_CAPACITY_B,
            "experiments_food_ratio"
        )

if __name__ == "__main__":
    main()
