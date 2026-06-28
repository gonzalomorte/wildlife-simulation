from core.vector import Vec2

# CONSTANTS
REFUGE_CAPACITY = 10
REFUGE_RADIUS = 30

class Refuge:
    def __init__(self, x, y, max_capacity=REFUGE_CAPACITY):
        """
        Constructor: creates a refuge at position (x, y) with maximum capacity
        and tracks boids inside it.
        """
        self.position = Vec2(x, y)
        self.boids_inside = []  # List of boids currently inside the refuge
        self.max_capacity = max_capacity
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
        Eject all boids from the refuge.
        Boids are placed at the refuge's current position.
        """
        ejected = self.boids_inside.copy()
        for boid in ejected:
            boid.position = Vec2(self.position.x, self.position.y)
            boid.in_refuge = False
        self.boids_inside = []
        return ejected

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
