from core.vector import Vec2

# Food system constants
FOOD_BOID_RATIO = 0.7  # Ratio of food items to boids 
FOOD_RESTORATION = 15  # Amount of food (health) restored when eaten
FOOD_RADIUS = 4  # Visual radius of food items
SATIETY_THRESHOLD = 85  # Threshold below which boids seek food (not when too full)
FOOD_SPAWN_RATE = 0.8  # Altered: Increased probability (was 0.3) for faster respawn attempts
FOOD_RESPAWN_BATCH = 10 # Added: Controls spawn speed. Number of food items the system tries to spawn per frame if needed.

class Food:
    """Represents a food item that boids can eat to restore their energy."""
    
    def __init__(self, x, y):
        """
        Constructor: creates a food item at position (x, y).
        
        Args:
            x (float): X coordinate of the food
            y (float): Y coordinate of the food
        """
        self.position = Vec2(x, y)
        self.radius = FOOD_RADIUS
        self.energy = FOOD_RESTORATION  # Amount of energy this food provides when eaten
