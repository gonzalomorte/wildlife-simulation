import random
from core.boid import Boid
from core.vector import Vec2
import math


class Predator(Boid):
    """Constructor: creates a predator at position (x, y) with a random
        initial velocity, zero acceleration, and specified movement
        parameters for max speed, max force, and perception radius.
        It chases prey and moves faster."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_speed = 3
        self.max_force = 0.3
        self.perception_radius = 100
        # Follow one target behavior
        self.target = None
        self.hunt_timer = 0
        self.hunt_duration = 300

    def find_nearest_prey(self, prey_list):
        """
        Return the closest prey to the predator.
        Ignores prey that are inside refuges (protected).
        """
        nearest = None
        min_distance = float("inf")

        for prey in prey_list:
            # Skip boids inside refuges
            if prey.in_refuge:
                continue
                
            distance = (prey.position - self.position).length()
            if distance < min_distance:
                min_distance = distance
                nearest = prey

        return nearest


    def chase(self, target):
        """
        Compute the steering force that moves the predator toward the target prey.
        """
        if target is None:
            return Vec2()

        direction = target.position - self.position
        desired = direction.set_magnitude(self.max_speed)

        steering = (desired - self.velocity).limit(self.max_force)
        return steering
    

    def hunt(self, prey_list):
        """
        Select the nearest prey, goes for it a fixed duration, and return the 
        chase steering force
        If no prey exists, the predator wanders randomly.
        If the timer runs out or the target is lost, a new prey is selected
        """

        if not prey_list:
            # Wander randomly when no prey is present
            angle = random.uniform(0, 2 * math.pi)
            self.target = None 
            return Vec2(math.cos(angle), math.sin(angle)) * 0.3

        # Step 1: pick nearest prey
        target = self.find_nearest_prey(prey_list)

        # Decide if a new target is needed 
        if self.target not in prey_list or self.hunt_timer <= 0:
            self.target = self.find_nearest_prey(prey_list)
            if self.target: 
                self.hunt_timer = self.hunt_duration # Reset the hunt timer


        # Step 2: chase it
        chase_force = self.chase(target)

        if self.target: 
            chase_force = self.chase(self.target)
            self.hunt_timer -= 1
            return chase_force
        else:
            angle = random.uniform(0,2*math.pi)
            return Vec2(math.cos(angle), math.sin(angle)) * 0.3

        return chase_force




