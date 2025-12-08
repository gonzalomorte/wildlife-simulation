from core.vector import Vec2
from core.boid import Boid

import random


class Simulation:
    def __init__(self, n_boids, width, height):  # CONSTRUCTOR -> public Simulation(int nBoids, int width, int height)
        self.width = width  # SELF -> THIS
        self.height = height

        self.boids = []  # List containing all Boid objects in the simulation
        for i in range(n_boids):  # for (int i = 0; i < nBoids; i++) 
            self.boids.append(Boid(random.randint(0, width), random.randint(0, height)))  # this.boids[i] = new Boid(random.nextInt(width), random.nextInt(height));

        self.separation = 1.5
        self.alignment = 1.0
        self.cohesion = 0.5


    def find_neighbors(self, target_boid):
        """
        Return a list of all boids that are within the perception
        radius of the given boid (target_boid).
        """
        neighbors = []
        for other_boid in self.boids:
            if other_boid is not target_boid:
                distance = (other_boid.position - target_boid.position).length()  # Find the vector between two positions and convert it into scalar distance
                if distance < target_boid.perception_radius:  # If it is within the perception radius
                    neighbors.append(other_boid)
        return neighbors
    

    def align(self, boid): 
        """
        Compute the alignment steering force.

        Alignment makes the boid steer toward the average 
        velocity direction of its neighbors.
        """
        neighbors = self.find_neighbors(boid)

        if not neighbors:
            return Vec2()  # (x=0, y=0)
            
        # Get the centroid
        avg_velocity = Vec2()
        for other in neighbors:
            avg_velocity = avg_velocity + other.velocity
        avg_velocity = avg_velocity / len(neighbors)  # Average velocity
        
        # Desired velocity: same direction, but at max speed
        desired = avg_velocity.set_magnitude(boid.max_speed)
        
        # Limit the steering force
        steering = desired - boid.velocity
        steering = steering.limit(boid.max_force)

        return steering
    

    def unite(self, boid): 
        """
        Compute the cohesion steering force.

        Cohesion makes the boid steer toward the average 
        position (center of mass) of its neighbors.
        """
        neighbors = self.find_neighbors(boid)

        if not neighbors:
            return Vec2()  # (x=0, y=0)
            
        # Get the centroid
        center = Vec2()
        for other in neighbors:
            center = center + other.position
        center = center / len(neighbors)  # Average position

        # Desired position
        desired = center - boid.position  # Reynolds formula: desired = average - current. Direction points toward the center of the group
        desired = desired.set_magnitude(boid.max_speed)  # The strength is limited to avoid the situation where all boids collapse into one single point and stop moving

        # Steering force: desired minus current velocity
        steering = desired - boid.velocity
        
        # Limit the steering force
        steering = steering.limit(boid.max_force)

        return steering
     
    
    def step(self):
        for boid in self.boids:
            boid.edges(self.width, self.height)
            alignment = self.align(boid)
            boid.accelerate(alignment)
            # cohesion = self.unite(boid)
            # boid.accelerate(cohesion)
            boid.update()

        
        """
            sep = Vec2()
            for other in neighbors:
                diff = boid.position - other.position
                sep = sep + (diff / (diff.length()**2 + 0.01))
            sep = sep.normalized()

            # Cohesion
            coh = Vec2()
            for other in neighbors:
                coh = coh + other.position
            coh = (coh / len(neighbors)) - boid.position
        """
        """
        # Apply weighted forces
        force = sep * self.separation + alignment * self.alignment + coh * self.cohesion
        boid.apply_force(force.limit(boid.max_force))
        """

        # Update all boids
        # 
        # for boid in self.boids:  # Updates and apply screen-wrapping to each boid

