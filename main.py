import pygame
from core.simulation import Simulation
from core.checkbox import Checkbox
from ui.render import draw_scene, update_sliders, sliders

N_BOIDS = 50
N_PREDATORS = 1

def main():
    width, height = 1200, 800  # Defining the size (both variables at the same time) 
    pygame.init()  # Set up pygame modules 
    win = pygame.display.set_mode((width, height))  #  Opens the display window 
    pygame.display.set_caption("Boids Simulation")  #  Title of the window
   
    # Checkboxes for drawing the perception radius and arrow directions
    checkbox_arrows = Checkbox(25, 210, "Arrows", checked=False)
    checkbox_perception = Checkbox(120, 210, "Radius", checked=False)

    simulation = Simulation(N_BOIDS, N_PREDATORS, width, height)  # Callback to the simulation construtor
    clock = pygame.time.Clock()  # Clock object for tracking the time in pygame


    running = True
    while running:  
        for event in pygame.event.get():  # Retrieves a list with all the events from the event queue (without parameters returns a list with all events since the last call) 
            if event.type == pygame.QUIT:  # In the loop we can handle each event individually. pygame.QUIT referes to attempt to close: e.g., close the 'X' in the window
                running = False
            # Handling checkboxes events
            checkbox_arrows.handle_event(event)
            checkbox_perception.handle_event(event)

        mouse_pressed = pygame.mouse.get_pressed()  # Retrieves the current state of the mouse buttons (0-0-0 left-middle-right states)
        mouse_pos = pygame.mouse.get_pos()  # Returns the current coordinates of the mouse

        # Update sliders based on mouse dragging
        update_sliders(mouse_pos, mouse_pressed)

        # Apply slider values to simulation
        simulation.separation = sliders["sep"][5]
        simulation.alignment = sliders["ali"][5]
        simulation.cohesion = sliders["coh"][5]
        simulation.max_force = sliders["mxf"][5]
        simulation.perception_radius = sliders["rad"][5]

        simulation.step()  # Advance simulation logic
        draw_scene(win, simulation.boids, simulation.predators, checkbox_perception, checkbox_arrows)

        clock.tick(60)  # Makes the loop to run at 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
