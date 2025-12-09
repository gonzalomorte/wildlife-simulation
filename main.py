import pygame
from core.simulation import Simulation
from ui.render import draw_scene, update_sliders, sliders

"""
TO-DO:
    - More realistic movement to boids (fuzzy)
"""

def main():
    width, height = 900, 600
    boids_num = 50
    
    pygame.init()
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Boids Simulation")

    sim = Simulation(boids_num, width, height)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Update sliders based on mouse dragging
        update_sliders(mouse_pos, mouse_pressed)

        # Apply slider values to simulation
        sim.w_sep = sliders["sep"][5]
        sim.w_ali = sliders["ali"][5]
        sim.w_coh = sliders["coh"][5]

        sim.step()
        draw_scene(win, sim.boids)

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
