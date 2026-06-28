import csv
import os
from datetime import datetime
from pathlib import Path


class StatsLogger:
    """
    Decoupled logger for recording simulation statistics at each tick.
    Creates CSV files with timestamps for easy experiment tracking.
    """
    
    # Column names for the CSV
    COLUMNS = [
        'tick',
        'alive_prey',
        'alive_predators',
        'prey_starved_cumulative',
        'prey_eaten_cumulative',
        'predators_starved_cumulative',
        'avg_prey_energy',
        'avg_predator_energy',
        'food_available'
    ]
    
    def __init__(self, log_dir='simulation_logs'):
        """
        Initialize the logger with a timestamped filename.
        
        Args:
            log_dir (str): Directory to store CSV files. Created if it doesn't exist.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'simulation_{timestamp}.csv'
        
        # Initialize CSV file with headers
        self._init_csv()
        
        self.tick_count = 0
        print(f"Logger initialized. Saving to: {self.log_file}")
    
    def _init_csv(self):
        """Create CSV file with header row."""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
            writer.writeheader()
    
    def log_tick(self, simulation):
        """
        Log statistics for the current simulation tick.
        
        Args:
            simulation (Simulation): The simulation object containing current state.
        """
        # Calculate average energies
        avg_prey_energy = (
            sum(b.food for b in simulation.boids) / len(simulation.boids)
            if simulation.boids else 0
        )
        avg_predator_energy = (
            sum(p.food for p in simulation.predators) / len(simulation.predators)
            if simulation.predators else 0
        )
        
        # Create data row
        row = {
            'tick': self.tick_count,
            'alive_prey': len(simulation.boids),
            'alive_predators': len(simulation.predators),
            'prey_starved_cumulative': simulation.boids_starved,
            'prey_eaten_cumulative': simulation.boids_eaten,
            'predators_starved_cumulative': simulation.predators_starved,
            'avg_prey_energy': round(avg_prey_energy, 2),
            'avg_predator_energy': round(avg_predator_energy, 2),
            'food_available': len(simulation.foods)
        }
        
        # Append to CSV
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
            writer.writerow(row)
        
        self.tick_count += 1
    
    def get_log_file(self):
        """Return the path to the current log file."""
        return str(self.log_file)