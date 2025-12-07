from core.vector import Vec2
from core.boid import Boid

import random

class Simulation:
    def __init__(self, n_boids, width, height):  # public Simulation(int nBoids, int width, int height)
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
                d = (other_boid.position - target_boid.position).length()
                if d < target_boid.perception:
                    neighbors.append(other_boid)
        return neighbors

    def step(self):
        for boid in self.boids:
            neigh = self.find_neighbors(boid)

            if len(neigh) > 0:

                # Separation
                sep = Vec2()
                for other in neigh:
                    diff = boid.position - other.position
                    sep = sep + (diff / (diff.length()**2 + 0.01))
                sep = sep.normalized()

                # Alignment
                ali = Vec2()
                for other in neigh:
                    ali = ali + other.velocity
                ali = (ali / len(neigh)) - boid.velocity

                # Cohesion
                coh = Vec2()
                for other in neigh:
                    coh = coh + other.position
                coh = (coh / len(neigh)) - boid.position

                # Apply weighted forces
                force = sep * self.separation + ali * self.alignment + coh * self.cohesion
                boid.apply_force(force.limit(boid.max_force))

        # Update all boids
        for boid in self.boids:
            boid.update()
            boid.edges(self.width, self.height)
