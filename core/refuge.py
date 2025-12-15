from core.vector import Vec2
import random

# CONSTANTS
REFUGE_CAPACITY = 10
REFUGE_MOVE_INTERVAL = 100  # seconds
REFUGE_RADIUS = 30

class Refuge:
    def __init__(self, x, y):
        """
        Constructor: creates a refuge at position (x, y) with maximum capacity
        and tracks boids inside it.
        """
        self.position = Vec2(x, y)
        self.boids_inside = []  # List of boids currently inside the refuge
        self.max_capacity = REFUGE_CAPACITY
        self.move_interval = REFUGE_MOVE_INTERVAL
        self.time_since_move = 0  # Counter to track time until next move
        self.radius = REFUGE_RADIUS

    def add_boid(self, boid):
        """
        Add a boid to the refuge if there is space available.
        Returns True if the boid was added, False otherwise.
        """
        if not self.is_full():
            self.boids_inside.append(boid)
            boid.in_refuge = True
            return True
        return False

    def remove_boid(self, boid):
        """
        Remove a boid from the refuge.
        """
        if boid in self.boids_inside:
            self.boids_inside.remove(boid)
            boid.in_refuge = False

    def eject_all_boids(self):
        """
        Eject all boids from the refuge when it moves.
        Boids are placed at the refuge's current position (before moving).
        """
        ejected = self.boids_inside.copy()
        for boid in ejected:
            boid.position = Vec2(self.position.x, self.position.y)
            boid.in_refuge = False
        self.boids_inside = []
        return ejected

    def update(self, width, height):
        """
        Update the refuge timer. When REFUGE_MOVE_INTERVAL seconds have passed,
        move the refuge to a random location.
        
        At 60 FPS, each frame is ~0.0167 seconds. We accumulate time in frames.
        """
        # Accumulate time: at 60 FPS, 1 second = 60 frames
        self.time_since_move += 1/60.0
        
        if self.time_since_move >= self.move_interval:
            # Eject boids before relocating so they reappear at the old spot
            self.eject_all_boids()
            self.move(width, height)
            self.time_since_move = 0

    def move(self, width, height):
        """
        Move the refuge to a random location on the screen.
        """
        self.position = Vec2(random.randint(self.radius, width-self.radius), random.randint(self.radius, height-self.radius))

    def is_full(self):
        """
        Check if the refuge is at max capacity.
        """
        return len(self.boids_inside) >= self.max_capacity

    def get_boid_count(self):
        """
        Return the number of boids currently inside the refuge.
        """
        return len(self.boids_inside)
