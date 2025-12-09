from core.boid import Boid
from core.vector import Vec2

class Predator(Boid):
    """A predator boid that chases prey and moves faster."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_speed = 6.0
        self.max_force = 0.3
        self.perception_radius = 150

    def hunt(self, prey_list):
        """Return a steering force toward the nearest prey."""
        if not prey_list:
            return Vec2()

        # Find nearest prey
        nearest = min(prey_list, key=lambda p: (p.position - self.position).length())
        desired = (nearest.position - self.position).set_magnitude(self.max_speed)
        steering = (desired - self.velocity).limit(self.max_force)
        return steering