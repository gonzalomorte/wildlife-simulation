from core.vector import Vec2

import math
import random

class Boid:
    def __init__(self, x, y):  # Constructor -> public Boid(int x, int y)
        """
        Constructor: creates a boid at position (x, y) with a random
        initial velocity, zero acceleration, and specified movement
        parameters for max speed, max force, and perception radius.
        """
        self.position = Vec2(x, y)  # Position
        angle = random.uniform(0, 2*math.pi)  # Angle between 0 and 2π (initial direction)
        self.velocity = Vec2(math.cos(angle), math.sin(angle))  # Unit vector in random direction
        self.acceleration = Vec2()  # Zero vector by default

        self.max_speed = 3
        self.max_force = 0.2
        self.perception_radius = 60  # radius that affect the boid behaviour
        
        # FOOD SYSTEM
        #self.food = random.uniform(20, 100)  # Food level (20-100, where 100 is full)
        self.food = 100
        self.time_since_food_decrease = 0  # Counter to decrease food every second
        self.in_refuge = False  # Track if boid is inside a refuge

        # STUCK DETECTION
        self.stuck_timer = 0
        self.ignore_food_timer = 0.0 

    def update(self):
        """
        Update the boid's motion for one simulation step.

        The velocity is adjusted using the current acceleration and not exceed the maximum speed. 
        The position is then updated based on this new velocity.
        The acceleration is reset so that new forces can accumulate during the next frame.
        """
        if not self.in_refuge:
            if self.velocity.length() < 1.0:
                self.stuck_timer += 1
            else:
                self.stuck_timer = 0
            if self.stuck_timer > 50:
                angle = random.uniform(0, 2*math.pi)
                wiggle = Vec2(math.cos(angle), math.sin(angle)) * self.max_force * 15
                self.apply_force(wiggle)
                self.ignore_food_timer = 1.5 
                self.stuck_timer = 0
                
        self.velocity = (self.velocity + self.acceleration).limit(self.max_speed)  # Update velocity and keep under max speed
        self.position = self.position + self.velocity
        self.acceleration = Vec2()  # Reset acceleration after updating position


    def accelerate(self, force):
        """
        Apply a force to the boid, changing its acceleration.
        """
        self.acceleration = force  # F = m*a (m=1) -> F = a
        
    def apply_force(self, force):
        self.acceleration = self.acceleration + force

    def update_food(self):
        """
        Update food level.
        Basal metabolism (Same as original: 1 unit/sec) + Kinetic cost (depends on velocity).
        """
        # 1. Basal Metabolism (Base Cost)
        # Original: 1 unit per 1.0 seconds.
        # Applied per frame (1 / 60), mathematically equivalent over one second.
        basal_metabolism = 1.0 / 60.0
        
        # 2. Kinetic Cost (Extra Cost)
        # Calculate current velocity
        speed = self.velocity.length()
        
        # Penalty factor:
        # Using speed**2 so moving slightly fast costs little,
        # but moving at maximum speed costs much more.
        # Adjustment: With factor 0.04 and speed 5 (max), extra cost is 1.0/sec.
        # Total at max speed = 2.0/sec (Double compared to standing still).
        kinetic_factor = 0.04 
        movement_cost = (speed ** 2 * kinetic_factor) / 60.0
        
        # Sum both costs
        total_loss = basal_metabolism + movement_cost
        
        # Apply the reduction
        self.food = max(0, self.food - total_loss)

    def edges(self, width, height):
        """
        Wraps the boid's position around the screen boundaries.
        If the boid moves off one side of the screen, it reappears on the
        opposite side.
        """
        if self.position.x > width:  
            self.position.x = 0
        elif self.position.x < 0:      
            self.position.x = width
        if self.position.y > height: 
            self.position.y = 0
        elif self.position.y < 0:      
            self.position.y = height
