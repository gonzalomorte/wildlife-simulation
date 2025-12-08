import pygame

# [x_pos, y_pos, width, min_value, max_value, default]
# x_pos & y_pos refer to the position of the slider from the top-left corner (0,0)
# width is the total size of the slider
# min_value is the value when is on the max left side of the slide
# max_value is the value when is on the max right side of the slide
# current value (set one by default)  
sliders = {  # DICTIONARY of slider configurations
    "sep": [10, 10, 200, 0.0, 3.0, 1.5],
    "ali": [10, 50, 200, 0.0, 3.0, 1.0],
    "coh": [10, 90, 200, 0.0, 3.0, 0.5],
    "mxf": [10, 130, 200, 0.0, 10, 0.2],
    "rad": [10, 170, 200, 0.0, 500, 80],
}


SLIDER_HITBOX_HEIGHT = 12
SLIDER_CURSOR_WIDTH = 10
SLIDER_CURSOR_HEIGHT = 16

active_slider = None  


def update_sliders(mouse_pos, mouse_pressed):
    """Update slider values when user drags them with the mouse."""
    global active_slider  # To use the variable defined in the module instead of a local one

    mouseX, mouseY = mouse_pos  # Assign the values to independent local variables

    # If user clicks, check if they clicked on a slider
    if mouse_pressed[0] and active_slider is None:  # mouse_pressed[0] is the left button (when we click over something)
        for name, (origin_x, origin_y, width, min_value, max_value, current_value) in sliders.items():  # Sliders.items() returns pairs (key, value). Dictionary key: name & Value is a tuple of 6 elements
            if ((origin_x <= mouseX <= width) and (origin_y <= mouseY <= origin_y + SLIDER_HITBOX_HEIGHT)) :  # Detects which slider is being used
                active_slider = name  # Save the slider being dragged

    # If dragging a slider
    if active_slider and mouse_pressed[0]:  # If active_slider has a proper value and the left click of the mouse is pressed
        origin_x, origin_y, width, min_value, max_value, current_value = sliders[active_slider]   

        relative_pos = (mouseX - origin_x) / width  # Normalizes the mouse position from the starting point (how far is from the left edge)
        relative_pos = max(0, min(1, relative_pos))  # relative_pos = a value between 0 and 1 (if relative_pos<0 -> 0; if relative_pos>1 -> 1; if 0<=relative_pos<=1 -> relative_pos). Then cannot be lower than 0 or higher than 1
        sliders[active_slider][5] = min_value + relative_pos * (max_value - min_value)  # Store the computed new  value of the slider active

    # Stop dragging when mouse released
    if not mouse_pressed[0]:
        active_slider = None


def draw_sliders(win):
    """Draw horizontal sliders and their labels."""
    font = pygame.font.SysFont(None, 24)

    for name, (origin_x, origin_y, width, min_value, max_value, current_value) in sliders.items():

        # Background bar
        pygame.draw.rect(win, (90, 90, 90), (origin_x, origin_y, width, SLIDER_HITBOX_HEIGHT))  # Draw the slider rectangle in the window 'w' with RGB(90,90,90) and the position and size fixed

        # Handle position
        relative_pos = (current_value - min_value) / (max_value - min_value)  # Normalize the value between 0 and 1
        slider_cursor = origin_x + relative_pos * width  # Computes the position of the slider cursor 

        # Handle
        pygame.draw.rect(win, (255, 255, 255), (slider_cursor - SLIDER_CURSOR_WIDTH/2, origin_y - 2, SLIDER_CURSOR_WIDTH, SLIDER_CURSOR_HEIGHT))  # Draw the slider cursor in the window 'w' with RGB(255,255,255) and the position and size fixed

        # Text label
        txt = font.render(f"{name}: {current_value:.2f}", True, (255, 255, 255))  # Text next to the slidebar (sep: 1.5)
        win.blit(txt, (origin_x + width + 20, origin_y - 2))  # Renders text into the display


def draw_boids(win, boids, checkbox_perception_radius, checkbox_arrow):
    "Support function to draw boids, perception radius and direction arrow"
    for b in boids:
        pygame.draw.circle(win, (200, 200, 255), (int(b.position.x), int(b.position.y)), 3)  # Surface, RGB, coordinates for the center of the circle, radius
        
        # Draw arrow direction only if enabled
        if checkbox_arrow.checked:
            arrow_head = b.position + b.velocity.normalized() * 15
            pygame.draw.line(win, (255, 255, 255), (int(b.position.x), int(b.position.y)), (int(arrow_head.x), int(arrow_head.y)), 1)

        # Draw perception radius only if enabled
        if checkbox_perception_radius.checked:
            pygame.draw.circle(win, (80, 80, 80 ), (int(b.position.x), int(b.position.y)), b.perception_radius, 1)
        


def draw_scene(win, boids, checkbox_perception_radius, checkbox_arrow):
    """Draw everything: background, boids, sliders."""
    win.fill((20, 20, 20))  # RGB fill for the background

    draw_boids(win, boids, checkbox_perception_radius, checkbox_arrow)
    draw_sliders(win)
    checkbox_perception_radius.draw(win)
    checkbox_arrow.draw(win)

    pygame.display.update()
