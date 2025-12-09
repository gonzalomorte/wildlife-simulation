from core.vector import Vec2

import math
import random

class Boid:
    # Obstacle avoidance constants
    MIN_DISTANCE_THRESHOLD = 0.001
    MIN_EDGE_DISTANCE = 0.1
    MAX_OBSTACLE_FORCE = 5.0
    
    def __init__(self, x, y):
        self.position = Vec2(x, y)
        angle = random.uniform(0, 2 * math.pi)
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

    def avoid_obstacles(self, obstacles):
        """Calculate avoidance force to steer away from obstacles."""
        avoidance = Vec2()
        obstacle_perception = 75
        
        for obstacle in obstacles:
            distance = (self.position - obstacle.position).length()
            
            if distance < obstacle.radius + obstacle_perception:
                # Calculate direction away from obstacle
                diff = self.position - obstacle.position
                diff_len = diff.length()
                
                if diff_len > self.MIN_DISTANCE_THRESHOLD:  # Not exactly at center
                    # Calculate distance from edge (negative if inside)
                    edge_distance = distance - obstacle.radius
                    
                    # Apply stronger force when closer, with special handling for inside obstacle
                    if edge_distance < 0:
                        # Inside obstacle - apply maximum force
                        strength = self.MAX_OBSTACLE_FORCE
                    else:
                        # Outside obstacle - inverse relationship with capped max
                        strength = min(1.0 / max(edge_distance, self.MIN_EDGE_DISTANCE), self.MAX_OBSTACLE_FORCE)
                    
                    avoidance = avoidance + diff.normalized() * strength
                else:
                    # Exactly at obstacle center - push in a random direction
                    angle = random.uniform(0, 2 * math.pi)
                    avoidance = avoidance + Vec2(math.cos(angle), math.sin(angle)) * self.MAX_OBSTACLE_FORCE
        
        if avoidance.length() > 0:
            return avoidance.normalized()
        return avoidance
    
    def edges(self, width, height):
        # "infinite window"
        if self.position.x > width:  self.position.x = 0
        if self.position.x < 0:     self.position.x = width
        if self.position.y > height: self.position.y = 0
        if self.position.y < 0:      self.position.y = height
