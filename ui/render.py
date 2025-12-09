import pygame

sliders = {
    "sep": [10, 10, 200, 0.0, 3.0, 1.5],
    "ali": [10, 50, 200, 0.0, 3.0, 1.0],
    "coh": [10, 90, 200, 0.0, 3.0, 0.5],
}

active_slider = None


def update_sliders(mouse_pos, mouse_pressed):
    """Update slider values when user drags them with the mouse."""
    global active_slider

    mx, my = mouse_pos

    # If user clicks, check if they clicked on a slider
    if mouse_pressed[0] and active_slider is None:
        for name, (x, y, w, mn, mxv, val) in sliders.items():
            if x <= mx <= x + w and y <= my <= y + 12:
                active_slider = name

    # If dragging a slider
    if active_slider and mouse_pressed[0]:
        x, y, w, mn, mxv, val = sliders[active_slider]

        t = (mx - x) / w
        t = max(0, min(1, t))  # clamp 0–1
        sliders[active_slider][5] = mn + t * (mxv - mn)

    # Stop dragging when mouse released
    if not mouse_pressed[0]:
        active_slider = None


def draw_sliders(win):
    font = pygame.font.SysFont(None, 24)

    for name, (x, y, w, mn, mxv, val) in sliders.items():

        # Background bar
        pygame.draw.rect(win, (90, 90, 90), (x, y, w, 12))

        # Handle position
        t = (val - mn) / (mxv - mn)
        hx = x + t * w

        # Handle
        pygame.draw.rect(win, (255, 255, 255), (hx - 5, y - 2, 10, 16))

        # Text label
        txt = font.render(f"{name}: {val:.2f}", True, (255, 255, 255))
        win.blit(txt, (x + w + 20, y - 2))



def draw_boids(win, boids):
    for b in boids:
        pygame.draw.circle(win, (200, 200, 255), (int(b.position.x), int(b.position.y)), 3)


def draw_obstacles(win, obstacles):
    """Draw obstacles as red circles."""
    for obs in obstacles:
        pygame.draw.circle(win, (200, 50, 50), (int(obs.position.x), int(obs.position.y)), int(obs.radius), 2)


def draw_scene(win, boids, obstacles=None):
    win.fill((20, 20, 20))

    # Draw obstacles first (background)
    if obstacles:
        draw_obstacles(win, obstacles)
    
    draw_boids(win, boids)
    draw_sliders(win)

    pygame.display.update()
