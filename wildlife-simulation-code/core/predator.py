import random
from core.boid import Boid
from core.vector import Vec2
import math

PREDATOR_ENERGY_GAIN = 15  # Energy restored when eating a boid

class Predator(Boid):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_speed = 2.5
        self.max_force = 0.3
        self.perception_radius = 80
        self.wander_angle = random.uniform(0, 2 * math.pi)
        self.target = None  # Track the current prey being hunted


    def find_nearest_prey(self, prey_list):
        """
        Return the closest prey to the predator within perception radius.
        Ignores prey that are inside refuges (protected).
        """
        nearest = None
        min_distance = float("inf")
        for prey in prey_list:
            if prey.in_refuge: continue
            distance = (prey.position - self.position).length()
            # Only consider prey within perception radius
            if distance < self.perception_radius and distance < min_distance:
                min_distance = distance
                nearest = prey
        return nearest

    def chase(self, target):
        if target is None: return Vec2()
        desired = (target.position - self.position).set_magnitude(self.max_speed)
        steering = (desired - self.velocity).limit(self.max_force)
        return steering
    
    def hunt(self, prey_list):
        """
        Select the nearest prey and return the chase steering force.
        If no prey exists or predator is too full to eat, wander randomly.
        """
        # Check if predator is too full to eat (would overflow energy)
        can_eat = (100 - self.food) >= PREDATOR_ENERGY_GAIN
        
        if not prey_list or not can_eat:
            # Wandering if no prey available or too full
            self.target = None  # Clear target when wandering
            self.wander_angle += random.uniform(-0.35, 0.35)
            direction = Vec2(math.cos(self.wander_angle), math.sin(self.wander_angle))
            return direction * 0.25

        # Step 1: pick nearest prey
        self.target = self.find_nearest_prey(prey_list)
        
        # If no valid target found (all in refuges), clear and wander
        if self.target is None:
            self.wander_angle += random.uniform(-0.35, 0.35)
            direction = Vec2(math.cos(self.wander_angle), math.sin(self.wander_angle))
            return direction * 0.25

        # Step 2: chase it
        chase_force = self.chase(self.target)

        return chase_force




