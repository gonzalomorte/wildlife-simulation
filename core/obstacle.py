from core.vector import Vec2
import math

class Obstacle:
    """A simple circular obstacle with a center and radius."""

    def __init__(self, x, y, radius):
        self.position = Vec2(x, y)
        self.radius = radius
