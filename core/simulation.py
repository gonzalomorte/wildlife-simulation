from core.vector import Vec2
from core.boid import Boid
from core.predator import Predator
from core.obstacle import Obstacle

import random

KILL_RADIUS = 10

class Simulation:
    def __init__(self, n_boids, n_predators, width, height):  # CONSTRUCTOR -> public Simulation(int nBoids, int width, int height)
        """
        Initialize a new Simulation instance.

        Args:
            n_boids (int): The number of boids to create.
            width (int): The width of the simulation canvas.
            height (int): The height of the simulation canvas.
        """
        self.width = width  # SELF -> THIS
        self.height = height

        # BOIDS
        self.boids = []  # List containing all Boid objects in the simulation
        for _ in range(n_boids):
            self.boids.append(Boid(random.randint(0, width), random.randint(0, height)))

        self.separation_weight = 1.5
        self.alignment_weight = 1.5
        self.cohesion_weight = 1.5
        self.max_force = 0.2
        self.perception_radius = 80
        
        # PREDATORS
        self.predators = []
        for _ in range(n_predators):
            self.predators.append(Predator(random.randint(0, width), random.randint(0, height)))

        # OBSTACLES
        self.obstacles = [
            Obstacle(300, 200, 40),
            Obstacle(600, 400, 60)
        ]


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
     

    def separate(self, boid): 
        """
        Compute the separation steering force.

        Separation makes the boid steer away from its neighbors to avoid collision.
        The force is inversely proportional to the distance.
        """
        neighbors = self.find_neighbors(boid)

        if not neighbors:
            return Vec2()  # (x=0, y=0)
            
        desired = Vec2()
        for other in neighbors:
            diff = (boid.position - other.position)
            distance = (other.position - boid.position).length()
            diff = diff * (1/distance)  # It is inversely proportional
            desired = desired + diff
        desired = desired / len(neighbors) # Average

        # Desired position
        desired = desired.set_magnitude(boid.max_speed)  # The strength is limited to avoid the situation where all boids collapse into one single point and stop moving

        # Steering force: desired minus current velocity
        steering = desired - boid.velocity
        
        # Limit the steering force
        steering = steering.limit(boid.max_force)

        return steering
    
    
    def step(self):
        """
        This method updates the entire flock in two phases to avoid
        sequential dependency between boids:
        """
        
        """
        1) INITIAL TEST WITHOUT REYNOLDS RULES
        for boid in self.boids:
            boid.edges(self.width, self.height)
            boid.update()
        """
        
        """
        2) INDEPENDENT TESTING (ALIGNMENT & COHESION)
        for boid in self.boids:
            boid.edges(self.width, self.height)
            
            # ALIGNMENT
            # alignment = self.align(boid)
            # boid.accelerate(alignment)
            
            # COHESION
            # cohesion = self.unite(boid)
            # boid.accelerate(cohesion)

            # SEPARATION
            separation = self.separate(boid)
            boid.accelerate(separation)
            
            boid.update()
        """

        """
        3) SIMULATING TOGETHER (ALL THE RULES WITH THE SAME WEIGHT)
        for boid in self.boids:
            boid.edges(self.width, self.height)
            
            alignment = self.align(boid)
            cohesion = self.unite(boid)
            separation = self.separate(boid)

            # Force accumulation
            force = alignment + cohesion + separation
            limited_force = force.limit(boid.max_force)
            boid.accelerate(limited_force)

            boid.update()
        """
        
        """
        4) SIMULATING TOGETHER (ALL THE RULES WITH THE SAME WEIGHT)
        for boid in self.boids:
            boid.edges(self.width, self.height)
            
            alignment = self.align(boid)
            cohesion = self.unite(boid)
            separation = self.separate(boid)
        
            force = (separation * self.separation) + (alignment * self.alignment) + (cohesion * self.cohesion) # Apply weighted forces
            limited_force = force.limit(boid.max_force)
            boid.accelerate(limited_force)

            boid.update()
        """
        
        """
        5) SOLVING SEQUENTIAL DEPENDENCY
        """
        all_forces = []
        # Phase 1: Calculate all steering forces based on the current state of the flock
        for boid in self.boids:
            boid.max_force = self.max_force
            boid.perception_radius = self.perception_radius

            alignment = self.align(boid)
            cohesion = self.unite(boid)
            separation = self.separate(boid)
            
            # Apply weights to each force
            force = (separation * self.separation_weight) + (alignment * self.alignment_weight) + (cohesion * self.cohesion_weight)
                
            # Limit the final force and store it
            limited_force = force.limit(boid.max_force)
            all_forces.append(limited_force)

        # Phase 2: Apply the calculated forces to update all boids simultaneously
        for i, boid in enumerate(self.boids):
            boid.edges(self.width, self.height)
            boid.accelerate(all_forces[i])
            boid.update()

        # Phase 3: Predators -> compute + update
        for predator in self.predators:
            predator.edges(self.width, self.height)
            direction = predator.hunt(self.boids)
            predator.accelerate(direction)
            predator.update()

        # Phase 4: Remove eaten boids
        for predator in self.predators:
            remaining_boids = []
            for boid in self.boids:
                distance = (predator.position - boid.position).length()
                if distance > KILL_RADIUS:
                    remaining_boids.append(boid)
                # else the boid is "eaten" → not added back

            self.boids = remaining_boids
                