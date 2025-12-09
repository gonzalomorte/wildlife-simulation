from core.vector import Vec2

class Obstacle:
    def __init__(self, x, y, radius=30):
        self.position = Vec2(x, y)
        self.radius = radius
    
    def contains_point(self, point):
        """Check if a point is inside the obstacle."""
        distance = (point - self.position).length()
        return distance < self.radius
    
    def distance_to_point(self, point):
        """Calculate distance from point to obstacle edge."""
        center_dist = (point - self.position).length()
        return max(0, center_dist - self.radius)
