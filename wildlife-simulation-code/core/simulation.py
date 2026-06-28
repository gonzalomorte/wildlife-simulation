from core.vector import Vec2
from core.boid import Boid
from core.predator import Predator
from core.obstacle import Obstacle
from core.refuge import Refuge, REFUGE_RADIUS, REFUGE_CAPACITY
from core.food import Food, FOOD_BOID_RATIO, FOOD_RESTORATION, SATIETY_THRESHOLD, FOOD_SPAWN_RATE, FOOD_RESPAWN_BATCH
from core.map_loader import get_map
from core.predator import PREDATOR_ENERGY_GAIN
from core.experiment_logger import ExperimentLogger
from core.stats_logger import StatsLogger

import random
import time

KILL_RADIUS = 10
OBSTACLE_AVOIDANCE_WEIGHT = 5
OBSTACLE_AVOIDANCE_PRIORITY_THRESHOLD = 0.3
REFUGE_FOOD_THRESHOLD = 50  # Threshold for leaving refuges
VISUAL_SIZE_MARGIN = 20  # Extra margin for bird shape visual size because of how they are drawn

class Simulation:
    def __init__(self, n_boids, n_predators, width, height, map_index=None, run_id=None, log_filepath="experiments.csv", 
                 refuge_capacity=None, food_ratio=None):
        """
        Initialize a new Simulation instance.

        Args:
            n_boids (int): The number of boids to create.
            n_predators (int): The number of predators to create.
            width (int): The width of the simulation canvas.
            height (int): The height of the simulation canvas.
            map_index (int, optional): Index of the map to load (0-10). If None, generates random obstacles and refuges.
            run_id (int, optional): ID for experiment logging. If None, logging is disabled.
            log_filepath (str): Path to CSV file for logging. Defaults to "experiments.csv"
            refuge_capacity (int, optional): Capacity per refuge. If None, uses default (10).
            food_ratio (float, optional): Food to boid ratio. If None, uses default (0.7).
        """
        self.width = width  # SELF -> THIS
        self.height = height
        
        # Store experiment configuration
        self.refuge_capacity = refuge_capacity if refuge_capacity is not None else REFUGE_CAPACITY
        self.food_ratio = food_ratio if food_ratio is not None else FOOD_BOID_RATIO

        # BOIDS
        self.boids = []  # List containing all Boid objects in the simulation
        for _ in range(n_boids):
            self.boids.append(Boid(random.randint(0, width), random.randint(0, height)))

        self.separation_weight = 1.25
        self.alignment_weight = 1.75
        self.cohesion_weight = 2.0
        self.obstacle_avoidance_weight = OBSTACLE_AVOIDANCE_WEIGHT
        self.food_seeking_weight = 3.0
        self.max_force = 0.2
        
        # PREDATORS
        self.predators = []
        for _ in range(n_predators):
            self.predators.append(Predator(random.randint(0, width), random.randint(0, height)))
            self.obstacle_avoidance_weight = OBSTACLE_AVOIDANCE_WEIGHT
            self.hunt_weight = 3.0

        # STATISTICS
        self.initial_boids = n_boids
        self.initial_predators = n_predators
        self.boids_starved = 0
        self.boids_eaten = 0
        self.predators_starved = 0
        self.start_time = time.perf_counter()
        self.step_count = 0
        self.history = {
            "boids_alive": [],
            "predators_alive": [],
            "foods": [],
        }
        
        # EXPERIMENT LOGGING
        self.logger = None
        self.log_interval = 1.0  # Log every 1 second
        self.next_log_time = 0.0  # Next simulation time (in seconds) to log
        if run_id is not None:
            self.logger = ExperimentLogger(
                run_id, 
                log_filepath,
                metadata={
                    "map_id": map_index,
                    "initial_boids": n_boids,
                    "initial_predators": n_predators,
                    "refuge_capacity": self.refuge_capacity,
                    "food_ratio": self.food_ratio,
                }
            )
        
        # STATS LOGGING - Always log tick-by-tick data to individual CSV files
        self.stats_logger = StatsLogger()
        
        # OBSTACLES AND REFUGES
        if map_index is not None:
            # Load map from file
            map_data = get_map(map_index)
            if map_data is None:
                raise ValueError(f"Map with index {map_index} not found. Valid indices are 0-9.")
            
            # Load obstacles from map
            self.obstacles = [
                Obstacle(obs['x'], obs['y'], obs['radius'])
                for obs in map_data['obstacles']
            ]
            
            # Load refuges from map
            self.refuges = [
                Refuge(ref['x'], ref['y'], max_capacity=self.refuge_capacity)
                for ref in map_data['refuges']
            ]
            
            print(f"Loaded map {map_index}: {map_data['name']} - {map_data['description']}")
        else:
            # Generate random obstacles and refuges (default behavior)
            self.obstacles = [
                Obstacle(random.randint(50, width - 50), random.randint(50, height - 50), random.randint(30, 70)),
                Obstacle(random.randint(50, width - 50), random.randint(50, height - 50), random.randint(30, 70))
            ]

            self.refuges = [
                Refuge(random.randint(REFUGE_RADIUS, width - REFUGE_RADIUS), random.randint(REFUGE_RADIUS, height - REFUGE_RADIUS), max_capacity=self.refuge_capacity)
            ]
        
        # FOOD
        self.foods = []    
        self.food_respawn_counter = 0

        # Create initial food based on configured food_ratio
        initial_food_count = int(n_boids * self.food_ratio)
        for _ in range(initial_food_count):
            self.spawn_food(force=True)

    
    def spawn_food(self, force=False):
        random.seed() # Added: Resets random generator to fix static position bug caused by render.py
        max_food = int(len(self.boids) * self.food_ratio)
        
        boid_obstacle_radius = 90
        if len(self.boids) > 0:
            boid_obstacle_radius = self.boids[0].perception_radius

        current_food = len(self.foods) # Added: Get current food count
        deficit = max_food - current_food # Added: Calculate how many are missing

        if deficit > 0 and (force or random.random() < FOOD_SPAWN_RATE): # Altered: Check deficit instead of just len < max
            
            items_to_spawn = deficit if force else min(deficit, FOOD_RESPAWN_BATCH) # Added: Calculate batch size
            
            for _ in range(items_to_spawn): # Added: Loop for the number of items we want to add this frame
                for _ in range(20): # Altered: Inner loop to find valid position (increased attempts)
                    x, y = random.randint(20, self.width-20), random.randint(20, self.height-20)
                    valid = True
                    for obs in self.obstacles:
                        if (Vec2(x,y) - obs.position).length() < obs.radius + boid_obstacle_radius: 
                            valid = False
                            break
                    
                    if valid:
                        for ref in self.refuges:
                            if (Vec2(x,y) - ref.position).length() < ref.radius + 10: 
                                valid = False
                                break
                                
                    if valid: 
                        self.foods.append(Food(x, y))
                        break # Altered: Break implies success for this item, continues to next item in batch
    
    def check_food_collision(self):
            """Handle collisions between boids and food and update boid energy.
            Boids eat only if hungry (below SATIETY_THRESHOLD) and not inside a refuge.
            """
            remaining_foods = []
            for food in self.foods:
                eaten = False
                for boid in self.boids:
                    if boid.food < SATIETY_THRESHOLD and not boid.in_refuge:
                        distance = (boid.position - food.position).length()
                        # Simple proximity collision: within food radius + small buffer
                        if distance <= (food.radius + 6):
                            boid.food = min(100, boid.food + food.energy)
                            eaten = True
                            break
                if not eaten:
                    remaining_foods.append(food)
            self.foods = remaining_foods

    def find_neighbors(self, target_boid):
        """
        Return a list of all boids that are within the perception
        radius of the given boid (target_boid).
        Excludes boids inside refuges (they're invisible).
        """
        neighbors = []
        for other_boid in self.boids:
            if other_boid is not target_boid and not other_boid.in_refuge:
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
            
            # Prevent from dividing by zero
            if distance < 0.001:
                distance = 0.001
            
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


    def find_obstacles(self, boid, safety_margin=10):
        obstacles = []
        
        for obstacle in self.obstacles:
            distance_center = (boid.position - obstacle.position).length()            

            # distance_edge = distance_center - obstacle_radius - margin
            distance_edge = distance_center - obstacle.radius - safety_margin
            
            if (distance_edge < boid.perception_radius):
                obstacles.append(obstacle)

        return obstacles


    def avoid_obstacles(self, boid, safety_margin=10):
        obstacles = self.find_obstacles(boid, safety_margin)

        if not obstacles:
            return Vec2()
        
        desired = Vec2()
        for obstacle in obstacles:
            diff = (boid.position - (obstacle.position + Vec2(obstacle.radius + safety_margin)))
            distance_center = (obstacle.position - boid.position).length()
            distance_edge = distance_center - obstacle.radius - safety_margin
            # Prevent from dividing by zero
            if distance_edge < 0.001:
                distance_edge = 0.001

            diff = diff * (1/distance_edge*distance_edge)
            desired = desired + diff
        desired = desired / len(obstacles)

        # Adjust the vector's length (same direction but at maximum speed)
        desired = desired.set_magnitude(boid.max_speed)
        
        # Steering force: desired minus current velocity (Reynolds)
        steering = desired - boid.velocity

        # Limit the steering force
        steering = steering.limit(boid.max_force)

        return steering
            
    
    def find_refuge(self, boid):
        """
        Compute the refuge searching force.
        If boid food > 15 , it looks for nearby refuges.
        If refuge is visible and has space, steer toward it.
        """
        if boid.food <= REFUGE_FOOD_THRESHOLD or boid.in_refuge:
            return Vec2()  # Don't look for refuge if hungry or already inside
        
        # Find nearby refuges
        for refuge in self.refuges:
            distance = (boid.position - refuge.position).length()
            
            if distance < boid.perception_radius and not refuge.is_full():
                # Desired velocity: steer toward refuge at max speed
                desired = (refuge.position - boid.position)
                desired = desired.set_magnitude(boid.max_speed)
                
                # Steering force
                steering = desired - boid.velocity
                steering = steering.limit(boid.max_force)
                
                return steering
        
        return Vec2()

    def find_food(self, boid):
        """
        Compute the food seeking steering force.
        Boids look for nearby food and steer toward it.
        More urgent when food is low.
        """
        # Don't seek food if eating would overflow
        if 100 - boid.food < FOOD_RESTORATION:
            return Vec2()
        
        # Find nearby food
        nearest_food = None
        nearest_distance = float('inf')
        
        for food in self.foods:
            distance = (boid.position - food.position).length()
            
            if distance < boid.perception_radius and distance < nearest_distance:
                nearest_food = food
                nearest_distance = distance
        
        if nearest_food:
            # Desired velocity: steer toward food at max speed
            desired = (nearest_food.position - boid.position)
            desired = desired.set_magnitude(boid.max_speed)
            
            # Steering force
            steering = desired - boid.velocity
            steering = steering.limit(boid.max_force)
            
            return steering
        
        return Vec2()

    def check_refuge_entry(self):
        """
        Check if boids should enter refuges or leave them based on food level.
        """
        # Handle boids entering refuges
        for boid in self.boids:
            if not boid.in_refuge and boid.food > REFUGE_FOOD_THRESHOLD:
                # Check if boid is at any refuge location
                for refuge in self.refuges:
                    distance = (boid.position - refuge.position).length()
                    if distance < refuge.radius:
                        # Try to add boid to refuge
                        if refuge.add_boid(boid):
                            break  # Boid entered, move to next boid

        # Handle boids leaving refuges (because food <= threshold)
        for refuge in self.refuges:
            boids_to_remove = []
            for boid in refuge.boids_inside:
                if boid.food <= REFUGE_FOOD_THRESHOLD:
                    boids_to_remove.append(boid)
            
            for boid in boids_to_remove:
                refuge.remove_boid(boid)

    def remove_starving_animals(self):
        """
        Remove animals that have starved (food <= 0).
        """
        remaining_boids = []
        for boid in self.boids:
            if boid.food > 0:
                remaining_boids.append(boid)
            else:
                self.boids_starved += 1
        self.boids = remaining_boids

        remaining_predators = []
        for predator in self.predators:
            if predator.food > 0:
                remaining_predators.append(predator)
            else:
                self.predators_starved += 1

        self.predators = remaining_predators

    def _record_step_metrics(self):
        """Store per-step counts for plotting at the end."""
        self.history["boids_alive"].append(len(self.boids))
        self.history["predators_alive"].append(len(self.predators))
        self.history["foods"].append(len(self.foods))
        
        # Log to CSV every log_interval seconds
        if self.logger is not None:
            elapsed = time.perf_counter() - self.start_time
            while elapsed >= self.next_log_time:
                metrics = self._calculate_metrics()
                self.logger.log_metrics(self.next_log_time, metrics)
                self.next_log_time += self.log_interval
    
    def _calculate_metrics(self):
        """Calculate all relevant metrics for the current simulation state."""
        metrics = {
            "sep": self.separation_weight,
            "ali": self.alignment_weight,
            "coh": self.cohesion_weight,
            "boids_alive": len(self.boids),
            "boids_eaten": self.boids_eaten,
            "boids_starved": self.boids_starved,
            "boids_in_refuge": sum(1 for r in self.refuges for _ in r.boids_inside),
            "predators_alive": len(self.predators),
            "predators_starved": self.predators_starved,
            "food_available": len(self.foods),
        }
        
        # Calculate boid-based metrics only if boids exist
        if self.boids:
            # Average distance between boids
            total_distance = 0
            pair_count = 0
            for i, b1 in enumerate(self.boids):
                for b2 in self.boids[i+1:]:
                    total_distance += (b1.position - b2.position).length()
                    pair_count += 1
            metrics["avg_boid_distance"] = total_distance / pair_count if pair_count > 0 else 0
            
            # Average velocity
            avg_vel = sum(b.velocity.length() for b in self.boids) / len(self.boids)
            metrics["avg_boid_velocity"] = avg_vel
            
            # Average separation (distance from center of mass)
            center_x = sum(b.position.x for b in self.boids) / len(self.boids)
            center_y = sum(b.position.y for b in self.boids) / len(self.boids)
            center = Vec2(center_x, center_y)
            
            distances_to_center = [(b.position - center).length() for b in self.boids]
            metrics["avg_boid_separation"] = sum(distances_to_center) / len(self.boids)
            metrics["center_of_mass_x"] = center_x
            metrics["center_of_mass_y"] = center_y
            metrics["max_boid_distance_to_center"] = max(distances_to_center)
            metrics["min_boid_distance_to_center"] = min(distances_to_center)
            
            # Average food level
            avg_food = sum(b.food for b in self.boids) / len(self.boids)
            metrics["avg_boid_food_level"] = avg_food
        else:
            # All zeros if no boids
            metrics["avg_boid_distance"] = 0
            metrics["avg_boid_velocity"] = 0
            metrics["avg_boid_separation"] = 0
            metrics["center_of_mass_x"] = 0
            metrics["center_of_mass_y"] = 0
            metrics["max_boid_distance_to_center"] = 0
            metrics["min_boid_distance_to_center"] = 0
            metrics["avg_boid_food_level"] = 0
        
        return metrics

    def get_stats(self):
        """Return a dict with run statistics for reporting/plotting."""
        elapsed = time.perf_counter() - self.start_time
        return {
            "initial_boids": self.initial_boids,
            "initial_predators": self.initial_predators,
            "boids_alive": len(self.boids),
            "predators_alive": len(self.predators),
            "boids_starved": self.boids_starved,
            "boids_eaten": self.boids_eaten,
            "predators_starved": self.predators_starved,
            "steps": self.step_count,
            "seconds": elapsed,
            "history": self.history,
        }

    def _handle_food_eating(self):
        """Check collisions between boids and food, handle eating.
        Boids only eat if they're hungry (below satiety threshold) and not in refuge."""
        remaining_food = []
        
        for food in self.foods:
            food_eaten = False
            for boid in self.boids:
                # Only eat if hungry and not in refuge
                if boid.food < SATIETY_THRESHOLD and not boid.in_refuge:
                    distance = (boid.position - food.position).length()
                    # Collision detection: boid speed + food radius + buffer
                    if distance < (boid.posi + food.radius + 5):
                        boid.food = min(100, boid.food + food.energy)  # Cap at 100, use food.energy
                        food_eaten = True
                        break
            
            if not food_eaten:
                remaining_food.append(food)
        
        self.foods = remaining_food

    def step(self):
        """
        This method updates the entire flock in multiple phases to avoid
        sequential dependency between boids.
        
        Phase 1: Food update and refuge management
        Phase 2: Calculate all steering forces
        Phase 3: Apply forces and update boids
        Phase 4: Predators
        Phase 5: Cleanup (eaten/starved boids)
        """
        # Phase 0: Update food for all boids
        for boid in self.boids:
            boid.update_food()

        for predator in self.predators:
            predator.update_food()

        # Phase 0.5: Handle boid entry/exit from refuges
        self.check_refuge_entry()

        # Try spawning food to maintain target population (after possible consumption)
        self.spawn_food()
        
        # Allow boids to eat food after hunger updates
        self.check_food_collision()
        
        all_forces = []
        # Phase 1: Calculate all steering forces based on the current state of the flock
        # Only for boids NOT in refuges
        for boid in self.boids:
            if boid.in_refuge:
                all_forces.append(Vec2())  # No movement for boids in refuges
                continue

            alignment = self.align(boid)
            cohesion = self.unite(boid)
            separation = self.separate(boid)
            obstacle_avoidance = self.avoid_obstacles(boid)
            refuge_searching = self.find_refuge(boid)
            food_seeking = self.find_food(boid)      

            if obstacle_avoidance.length() > OBSTACLE_AVOIDANCE_PRIORITY_THRESHOLD * boid.max_force:
                # If it is about to crash, gives priority
                force = obstacle_avoidance
            else:
                # Apply weights to each force including food seeking
                force = (separation * self.separation_weight) + (alignment * self.alignment_weight) + (cohesion * self.cohesion_weight) + (obstacle_avoidance * self.obstacle_avoidance_weight) + refuge_searching + (food_seeking * self.food_seeking_weight)        
            # Limit the final force and store it
            limited_force = force.limit(boid.max_force)
            all_forces.append(limited_force)

        # Phase 2: Apply the calculated forces to update all boids simultaneously
        for i, boid in enumerate(self.boids):
            if not boid.in_refuge:
                boid.edges(self.width, self.height)
                boid.accelerate(all_forces[i])
                boid.update()

        # Phase 3: Predators -> compute + update
        for predator in self.predators:
            predator.edges(self.width, self.height)
            predator.max_force = self.max_force
            obstacle_avoidance = self.avoid_obstacles(predator, safety_margin=25)
            
            nearby_boids = []
            for b in self.boids:
                distance = (predator.position - b.position).length()
                if (distance <= predator.perception_radius):
                    nearby_boids.append(b)
       
            direction = (
                obstacle_avoidance * self.obstacle_avoidance_weight +
                predator.hunt(nearby_boids) * self.hunt_weight
            )

            direction = direction.limit(predator.max_force)
       
            predator.accelerate(direction)
       
            predator.update()

         # Phase 4: Remove eaten boids and restore predator energy
        for predator in self.predators:
            remaining_boids = []
            for boid in self.boids:
                distance = (predator.position - boid.position).length()
                # Check if predator is too full to eat (would overflow)
                can_eat = (100 - predator.food) >= PREDATOR_ENERGY_GAIN
                
                if distance > KILL_RADIUS or boid.in_refuge or not can_eat:
                    remaining_boids.append(boid)
                else:
                    # Boid is eaten - restore predator energy
                    self.boids_eaten += 1
                    predator.food = min(100, predator.food + PREDATOR_ENERGY_GAIN)

            self.boids = remaining_boids

        # Phase 5: Remove starved animals
        self.remove_starving_animals()

        # Phase 6: Record step metrics for reporting
        self._record_step_metrics()
        self.step_count += 1
        
        # Log tick data to individual CSV file
        self.stats_logger.log_tick(self)