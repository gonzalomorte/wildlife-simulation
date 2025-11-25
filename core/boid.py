from core.vector import Vec2

import math
import random

class Boid:
    def __init__(self, x, y):
        self.position = Vec2(x, y)
        angle = random.uniform(0, 6.28)
        self.velocity = Vec2(math.cos(angle), math.sin(angle))
        self.acceleration = Vec2()

        self.max_speed = 3
        self.max_force = 0.015

        self.perception = 50  

    def update(self):
        self.velocity = (self.velocity + self.acceleration).limit(self.max_speed)
        self.position = self.position + self.velocity
        self.acceleration = Vec2()

    def apply_force(self, force):
        # you can extend this later
        self.acceleration = self.acceleration + force

    def edges(self, width, height):
        # world wrapping
        if self.position.x > width:  self.position.x = 0
        if self.position.x < 0:     self.position.x = width
        if self.position.y > height: self.position.y = 0
        if self.position.y < 0:      self.position.y = height
