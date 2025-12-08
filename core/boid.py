from core.vector import Vec2

import math
import random

class Boid:
    def __init__(self, x, y):  # Constructor -> public Boid(int x, int y)
        self.position = Vec2(x, y)  # Position 
        angle = random.uniform(0, 6.28)  # Angle between 0 and 2π (initial direction)
        self.velocity = Vec2(math.cos(angle), math.sin(angle))  # Unit vector pointing in the random direction
        self.acceleration = Vec2()  # Zero vector by default

        self.max_speed = 10
        self.max_force = 0.2
        self.perception_radius = 80  # radius that affect the boid behaviour

    def update(self):
        """
        Update the boid's motion for one simulation step.

        The velocity is adjusted using the current acceleration and not exceed the maximum speed. 
        The position is then updated based on this new velocity.
        The acceleration is reset so that new forces can accumulate during the next frame.
        """
        self.velocity = (self.velocity + self.acceleration).limit(self.max_speed)  # Increases the velocity but keeping under the maximum speed
        self.position = self.position + self.velocity
        self.acceleration = Vec2()  # Reset acceleration after updating position


    def apply_force(self, force):
        self.acceleration = self.acceleration + force  # F = m*a (m=1) -> F = a


    def accelerate(self, force):
        self.acceleration = force


    def edges(self, width, height):
        # world wrapping
        if self.position.x > width:  self.position.x = 0
        if self.position.x < 0:      self.position.x = width
        if self.position.y > height: self.position.y = 0
        if self.position.y < 0:      self.position.y = height
