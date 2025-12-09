from core.vector import Vec2
from core.boid import Boid
from core.obstacle import Obstacle

import random

class Simulation:
    def __init__(self, n_boids, width, height):
        self.width = width
        self.height = height
        self.boids = [Boid(random.randint(0, width), random.randint(0, height)) 
                      for _ in range(n_boids)]
        self.obstacles = []

        self.w_sep = 1.5
        self.w_ali = 1.0
        self.w_coh = 0.5
        self.w_obs = 2.0

    def add_obstacle(self, x, y, radius=30):
        """Add an obstacle at the specified position."""
        self.obstacles.append(Obstacle(x, y, radius))
    
    def neighbors(self, boid):
        ns = []
        for other in self.boids:
            if other is not boid:
                d = (other.position - boid.position).length()
                if d < boid.perception:
                    ns.append(other)
        return ns

    def step(self):
        for boid in self.boids:
            neigh = self.neighbors(boid)

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
                force = sep * self.w_sep + ali * self.w_ali + coh * self.w_coh
                boid.apply_force(force.limit(boid.max_force))
            
            # Obstacle avoidance (always applied)
            if len(self.obstacles) > 0:
                obs = boid.avoid_obstacles(self.obstacles)
                boid.apply_force(obs * self.w_obs)

        # Update all boids
        for boid in self.boids:
            boid.update()
            boid.edges(self.width, self.height)
