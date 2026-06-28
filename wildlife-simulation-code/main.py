import argparse
import time
import os

N_BOIDS = 10
N_PREDATORS = 1

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Wildlife Simulation with Boids')
    parser.add_argument(
        '-map', 
        type=int, 
        metavar='INDEX',
        help='Map index to load (0-10). If not specified, generates random obstacles and refuges.',
        choices=range(11),
        default=10
    )
    parser.add_argument(
        '--run-id',
        type=int,
        metavar='ID',
        help='Run ID for experiment logging. If provided, metrics are logged to experiments.csv',
        default=None
    )
    parser.add_argument(
        '--log-file',
        metavar='PATH',
        help='Path to CSV file for logging. Defaults to experiments.csv',
        default='experiments.csv'
    )
    parser.add_argument(
        '-sep',
        type=float,
        metavar='VALUE',
        help='Separation weight (0-3).'
    )
    parser.add_argument(
        '-ali',
        type=float,
        metavar='VALUE',
        help='Alignment weight (0-3).'
    )
    parser.add_argument(
        '-coh',
        type=float,
        metavar='VALUE',
        help='Cohesion weight (0-3).'
    )
    parser.add_argument(
        '--duration',
        type=int,
        metavar='SECONDS',
        help='Duration in seconds. If provided, simulation stops automatically after this time.',
        default=None
    )
    parser.add_argument(
        '--refuge-capacity',
        type=int,
        metavar='VALUE',
        help='Capacity per refuge. If not specified, uses default (10).',
        default=None
    )
    parser.add_argument(
        '--food-ratio',
        type=float,
        metavar='VALUE',
        help='Food to boid ratio. If not specified, uses default (0.7).',
        default=None
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run without GUI (faster for batch experiments).'
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Enable headless mode for batch experiments (must be before pygame import)
    headless = args.headless or args.run_id is not None
    if headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    
    # Import pygame after setting environment variable
    import pygame
    pygame.init()
    
    # Import simulation modules after pygame
    from core.simulation import Simulation
    from ui.render import draw_scene, update_sliders, sliders, update_checkboxes
    
    width, height = 1200, 800  # Defining the size (both variables at the same time) 
    win = pygame.display.set_mode((width, height))  #  Opens the display window 
    pygame.display.set_caption("Boids Simulation")  #  Title of the window

    simulation = Simulation(
        N_BOIDS, 
        N_PREDATORS, 
        width, 
        height, 
        map_index=args.map, 
        run_id=args.run_id, 
        log_filepath=args.log_file,
        refuge_capacity=args.refuge_capacity,
        food_ratio=args.food_ratio
    )  # Callback to the simulation construtor
    
    # Apply parameter overrides if provided
    if args.sep is not None:
        simulation.separation_weight = args.sep
    if args.ali is not None:
        simulation.alignment_weight = args.ali
    if args.coh is not None:
        simulation.cohesion_weight = args.coh
    
    clock = pygame.time.Clock()  # Clock object for tracking the time in pygame

    running = True
    end_reason = None
    start_time = time.perf_counter()
    while running:  
        elapsed = time.perf_counter() - start_time

        # Optional duration cap: only active when provided by CLI
        if args.duration is not None and elapsed >= args.duration:
            end_reason = "duration"
            break

        # Auto-stop if either species goes extinct
        if len(simulation.boids) == 0 or len(simulation.predators) == 0:
            end_reason = "extinction"
            break
        
        for event in pygame.event.get():  # Retrieves a list with all the events from the event queue 
            if not headless and event.type == pygame.QUIT:  # pygame.QUIT referes to attempt to close: e.g., close the 'X' in the window
                running = False
                end_reason = "quit"
            update_checkboxes(event)

        mouse_pressed = pygame.mouse.get_pressed()  # Retrieves the current state of the mouse buttons 
        mouse_pos = pygame.mouse.get_pos()  # Returns the current coordinates of the mouse

        # Update sliders based on mouse dragging
        update_sliders(mouse_pos, mouse_pressed)

        # Apply slider values to simulation (only if NOT running an experiment with fixed parameters)
        if args.run_id is None:
            simulation.separation_weight = sliders["sep"].current_value
            simulation.alignment_weight = sliders["ali"].current_value
            simulation.cohesion_weight = sliders["coh"].current_value


        simulation.step()  # Advance simulation logic
        draw_scene(win, simulation.boids, simulation.predators, simulation.obstacles, simulation.refuges, simulation.foods)  

        clock.tick(60)  # Makes the loop to run at 60 FPS

    # Ensure we log the final state regardless of how the loop ended
    if simulation.logger is not None:
        final_metrics = simulation._calculate_metrics()
        final_elapsed = time.perf_counter() - start_time
        simulation.logger.log_metrics(final_elapsed, final_metrics)

    stats = simulation.get_stats()
    pygame.quit()
    _print_stats(stats, end_reason)
    
    if simulation.logger is not None:
        print(f"\nExperiment data logged to: {simulation.logger.get_filepath()}")


def _print_stats(stats, end_reason=None):
    """Print end-of-run stats to the console."""
    print("\nSimulation summary")
    if end_reason:
        print(f"Ended because    : {end_reason}")
    print(f"Runtime          : {stats['seconds']:.2f}s")
    print(f"Steps            : {stats['steps']}")
    print(f"Boids start/alive: {stats['initial_boids']} -> {stats['boids_alive']}")
    print(f"Boids eaten      : {stats['boids_eaten']}")
    print(f"Boids starved    : {stats['boids_starved']}")
    print(f"Predators start/alive: {stats['initial_predators']} -> {stats['predators_alive']}")
    print(f"Predators starved    : {stats['predators_starved']}")


if __name__ == "__main__":
    main()