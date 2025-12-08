import math

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self):
        l = self.length()
        return self / l if l > 0 else Vec2()

    def limit(self, max_length):
        if self.length() > max_length:
            return self.normalized() * max_length
        return self

    def set_magnitude(self, new_mag):
        """
        Return a new vector with the same direction but the given magnitude.
        """
        current_mag = self.length()
        
        if current_mag == 0:
            return Vec2()  # avoid division by zero
        
        return self * (new_mag / current_mag)
