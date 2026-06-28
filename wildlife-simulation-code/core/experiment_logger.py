import csv
import os
from pathlib import Path

class ExperimentLogger:
    """Logs simulation metrics to CSV for experiment analysis."""
    
    def __init__(self, run_id, filepath="experiments.csv", metadata=None):
        """
        Initialize the logger.
        
        Args:
            run_id (int): Unique identifier for this run
            filepath (str): Path to the CSV file (will be created if doesn't exist)
        """
        self.run_id = run_id
        self.filepath = filepath
        self.file_exists = os.path.exists(filepath)
        self.metadata = metadata or {}
        
        # Define columns (keep only essentials for this experiment)
        self.fieldnames = [
            "run_id",
            "map_id",
            "initial_boids",
            "initial_predators",
            "refuge_capacity",
            "food_ratio",
            "timestamp_sec",
            "boids_alive",
            "predators_alive",
        ]
        
        # Create/append to CSV
        self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.file_exists:
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def log_metrics(self, timestamp_sec, metrics):
        """
        Log a row of metrics.
        
        Args:
            timestamp_sec (float): Simulation time in seconds
            metrics (dict): Dictionary with metric names and values
        """
        # Static metadata included on every row
        row = {
            "run_id": self.run_id,
            "timestamp_sec": round(timestamp_sec, 2),
            "map_id": self.metadata.get("map_id", ""),
            "initial_boids": self.metadata.get("initial_boids", ""),
            "initial_predators": self.metadata.get("initial_predators", ""),
            "refuge_capacity": self.metadata.get("refuge_capacity", ""),
            "food_ratio": self.metadata.get("food_ratio", ""),
        }

        # Add runtime metrics (skip fields already set)
        for field in self.fieldnames:
            if field not in row:
                row[field] = metrics.get(field, "")
        
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)
    
    def get_filepath(self):
        """Return the full path to the CSV file."""
        return os.path.abspath(self.filepath)
