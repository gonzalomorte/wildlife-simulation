from core.vector import Vec2
import math

class Obstacle:
    """Constructor: creates a obstacle at position (x, y) 
    with the specified radius."""

    def __init__(self, x, y, radius):
        self.position = Vec2(x, y)
        self.radius = radius
