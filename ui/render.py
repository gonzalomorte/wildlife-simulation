import pygame
from core.checkbox import Checkbox
from core.slider import Slider

# CONSTANTS
BOID_SIZE = 3
PREDATOR_SIZE = 8
OBSTACLE_SIZE = 30
ARROW_LENGTH = 15
active_slider = None  

sliders = {
    "sep": Slider(10, 10, 200, 0.0, 3.0, 1.5),
    "ali": Slider(10, 50, 200, 0.0, 3.0, 1.5),
    "coh": Slider(10, 90, 200, 0.0, 3.0, 1.5),
    "mxf": Slider(10, 130, 200, 0.0, 10, 0.2),
    "rad": Slider(10, 170, 200, 0.0, 500, 80),
}

# Checkboxes for drawing the perception radius and arrow directions
checkboxes = {
    "arr": Checkbox(25, 210, "Arrows", checked=False), 
    "rad": Checkbox(120, 210, "Radius", checked=False)
}


def update_sliders(mouse_pos, mouse_pressed):
    """Update slider values when user drags them with the mouse."""
    global active_slider  # To use the variable defined in the module instead of a local one

    mouseX, mouseY = mouse_pos  # Assign the values to independent local variables

    # Check if they clicked on a slider
    if mouse_pressed[0] and active_slider is None:  # mouse_pressed[0] is the left button (when we click over something)
        for name, slider in sliders.items():  # Sliders.items() returns pairs (key, value). Dictionary key: name & Value is a tuple of 6 elements
            if ((slider.x <= mouseX <= slider.x + slider.width) and (slider.y <= mouseY <= slider.y + Slider.HITBOX_HEIGHT)) :  # Detects which slider is being used
                active_slider = name  # Save the slider being dragged

    # If dragging a slider
    if active_slider and mouse_pressed[0]:  # If active_slider has a proper value and the left click of the mouse is pressed
        slider = sliders[active_slider]   
        slider.update(mouseX)
        
    # Stop dragging when mouse released
    if not mouse_pressed[0]:
        active_slider = None


def update_checkboxes(event):
    # Handling checkboxes events
    for checkbox in checkboxes.values():
        checkbox.handle_event(event)


def draw_sliders(win):
    """Draw horizontal sliders and their labels."""
    font = pygame.font.SysFont(None, 24)

    for name, slider in sliders.items():

        # Background bar
        pygame.draw.rect(win, (90, 90, 90), (slider.x, slider.y, slider.width, Slider.HITBOX_HEIGHT))  # Draw the slider rectangle in the window 'w' with RGB(90,90,90) and the position and size fixed

        # Handle position
        relative_pos = (slider.current_value - slider.min_value) / (slider.max_value - slider.min_value)  # Normalize the value between 0 and 1
        slider_cursor = slider.x + relative_pos * slider.width  # Computes the position of the slider cursor 

        # Handle
        pygame.draw.rect(win, (255, 255, 255), (slider_cursor - Slider.CURSOR_WIDTH/2, slider.y - 2, Slider.CURSOR_WIDTH, Slider.CURSOR_HEIGHT))  # Draw the slider cursor in the window 'w' with RGB(255,255,255) and the position and size fixed

        # Text label
        txt = font.render(f"{name}: {slider.current_value:.2f}", True, (255, 255, 255))  # Text next to the slidebar (sep: 1.5)
        win.blit(txt, (slider.x + slider.width + 20, slider.y - 2))  # Renders text into the display


def draw_checkboxes(win):
    for name, checkbox in checkboxes.items():
        # Draw square
        pygame.draw.rect(win, (255,255,255), checkbox.rect, 2)

        # Fill if checked
        if checkbox.checked:
            pygame.draw.rect(win, (255,255,255), checkbox.rect.inflate(-6, -6))

        # Draw text
        label = checkbox.font.render(checkbox.text, True, (255,255,255))
        win.blit(label, (checkbox.x + checkbox.size + 10, checkbox.y))
        


def draw_boids(win, boids):
    """Support function to draw boids, perception radius and direction arrow"""
    for b in boids:
        # Draw boids
        pygame.draw.circle(win, (200, 200, 255), (int(b.position.x), int(b.position.y)), BOID_SIZE)  # Surface, RGB, coordinates for the center of the circle, radius
        
        # Draw arrow direction only if enabled
        if checkboxes["arr"].checked:
            arrow_head = b.position + b.velocity.normalized() * ARROW_LENGTH
            pygame.draw.line(win, (255, 255, 255), (int(b.position.x), int(b.position.y)), (int(arrow_head.x), int(arrow_head.y)), 1)

        # Draw perception radius only if enabled
        if checkboxes["rad"].checked:
            pygame.draw.circle(win, (80, 80, 80 ), (int(b.position.x), int(b.position.y)), b.perception_radius, 1)
        

def draw_predators(win, predators):
    """Support function to draw predators"""
    for predator in predators:
        pygame.draw.circle(win, (255, 0, 0),(int(predator.position.x),int(predator.position.y)), PREDATOR_SIZE)


def draw_obstacles(win, obstacles):
    """Support function to draw obstacles"""
    for obstacle in obstacles:
        pygame.draw.circle(win, (125, 30, 17),(int(obstacle.position.x), int(obstacle.position.y)), OBSTACLE_SIZE)


def draw_scene(win, boids, predators, obstacles):
    """Draw everything: background, boids, predaators, obstacles, sliders, checkboxes..."""
    win.fill((20, 20, 20))  # RGB fill for the background

    draw_predators(win, predators)
    draw_obstacles(win, obstacles)
    draw_boids(win, boids)
    draw_sliders(win)
    draw_checkboxes(win)
    
    pygame.display.update()
