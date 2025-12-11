import pygame
pygame.init()  # Set up pygame modules 
from core.simulation import Simulation
from core.checkbox import Checkbox
from ui.render import draw_scene, update_sliders, sliders, update_checkboxes

N_BOIDS = 10
N_PREDATORS = 0

def main():
    width, height = 1200, 800  # Defining the size (both variables at the same time) 
    win = pygame.display.set_mode((width, height))  #  Opens the display window 
    pygame.display.set_caption("Boids Simulation")  #  Title of the window

    simulation = Simulation(N_BOIDS, N_PREDATORS, width, height)  # Callback to the simulation construtor
    clock = pygame.time.Clock()  # Clock object for tracking the time in pygame


    running = True
    while running:  
        for event in pygame.event.get():  # Retrieves a list with all the events from the event queue (without parameters returns a list with all events since the last call) 
            if event.type == pygame.QUIT:  # In the loop we can handle each event individually. pygame.QUIT referes to attempt to close: e.g., close the 'X' in the window
                running = False
    
            update_checkboxes(event)

        mouse_pressed = pygame.mouse.get_pressed()  # Retrieves the current state of the mouse buttons (0-0-0 left-middle-right states)
        mouse_pos = pygame.mouse.get_pos()  # Returns the current coordinates of the mouse

        # Update sliders based on mouse dragging
        update_sliders(mouse_pos, mouse_pressed)

        # Apply slider values to simulation
        simulation.separation_weight = sliders["sep"].current_value
        simulation.alignment_weight = sliders["ali"].current_value
        simulation.cohesion_weight = sliders["coh"].current_value
        simulation.max_force = sliders["mxf"].current_value
        simulation.perception_radius = sliders["rad"].current_value

        simulation.step()  # Advance simulation logic
        draw_scene(win, simulation.boids, simulation.predators, simulation.obstacles)

        clock.tick(60)  # Makes the loop to run at 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
