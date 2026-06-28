import pygame
import math
from core.checkbox import Checkbox
from core.slider import Slider
from core.simulation import VISUAL_SIZE_MARGIN
from core.predator import PREDATOR_ENERGY_GAIN

# CONSTANTS
BOID_SIZE = 8
PREDATOR_SIZE = 12
ARROW_LENGTH = 15
active_slider = None

# Initialize fonts once
slider_font = None
refuge_font = None  

sliders = {
    "sep": Slider(10, 10, 200, 0.0, 3.0, 1.25),
    "ali": Slider(10, 50, 200, 0.0, 3.0, 1.75),
    "coh": Slider(10, 90, 200, 0.0, 3.0, 2.0),
}

checkboxes = {
    "arr": Checkbox(25, 120, "Arrows", checked=False), 
    "rad": Checkbox(120, 120, "Radius", checked=False)
}


def update_sliders(mouse_pos, mouse_pressed):
    global active_slider
    mouseX, mouseY = mouse_pos
    if mouse_pressed[0] and active_slider is None:
        for name, slider in sliders.items():
            if ((slider.x <= mouseX <= slider.x + slider.width) and (slider.y <= mouseY <= slider.y + Slider.HITBOX_HEIGHT)):
                active_slider = name
    if active_slider and mouse_pressed[0]:
        sliders[active_slider].update(mouseX)
    if not mouse_pressed[0]:
        active_slider = None


def update_checkboxes(event):
    for checkbox in checkboxes.values():
        checkbox.handle_event(event)


def draw_sliders(win):
    global slider_font
    if slider_font is None:
        slider_font = pygame.font.SysFont(None, 24)
    for name, slider in sliders.items():
        pygame.draw.rect(win, (90, 90, 90), (slider.x, slider.y, slider.width, Slider.HITBOX_HEIGHT))
        relative_pos = (slider.current_value - slider.min_value) / (slider.max_value - slider.min_value)
        slider_cursor = slider.x + relative_pos * slider.width
        pygame.draw.rect(win, (255, 255, 255), (slider_cursor - Slider.CURSOR_WIDTH/2, slider.y - 2, Slider.CURSOR_WIDTH, Slider.CURSOR_HEIGHT))
        txt = slider_font.render(f"{name}: {slider.current_value:.2f}", True, (255, 255, 255))
        win.blit(txt, (slider.x + slider.width + 20, slider.y - 2))


def draw_checkboxes(win):
    for checkbox in checkboxes.values():
        pygame.draw.rect(win, (255,255,255), checkbox.rect, 2)
        if checkbox.checked:
            pygame.draw.rect(win, (255,255,255), checkbox.rect.inflate(-6, -6))
        label = checkbox.font.render(checkbox.text, True, (255,255,255))
        win.blit(label, (checkbox.x + checkbox.size + 10, checkbox.y))


def draw_food(win, foods):
    """Draw food as seeds or berries."""
    for food in foods:
        # Food appears as yellow-green seeds/berries
        pygame.draw.circle(win, (255, 200, 50), (int(food.position.x), int(food.position.y)), food.radius)
        # Add a highlight for depth
        pygame.draw.circle(win, (255, 220, 100), (int(food.position.x) - 1, int(food.position.y) - 1), 1)

def draw_energy_bar(win, entity, color, width, y_offset, height=2):
    health_percentage = max(0, min(100, entity.food)) / 100.0
    bar_x = int(entity.position.x) - width // 2
    bar_y = int(entity.position.y) - y_offset
    pygame.draw.rect(win, (50, 50, 50), (bar_x, bar_y, width, height))
    pygame.draw.rect(win, color, (bar_x, bar_y, int(width * health_percentage), height))

def draw_bird_shape(win, position, velocity, color, size):
    """Draw a simple bird shape pointing in the direction of movement."""
    if velocity.length() > 0.1:
        angle = math.atan2(velocity.y, velocity.x)
    else:
        angle = 0
    
    def rotate_point(x, y):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (
            position.x + x * cos_a - y * sin_a,
            position.y + x * sin_a + y * cos_a
        )
    
    # Simple bird body (triangle pointing forward)
    head = rotate_point(size, 0)
    body_left = rotate_point(-size * 0.4, size * 0.5)
    body_right = rotate_point(-size * 0.4, -size * 0.5)
    
    # Wings
    left_wing = rotate_point(-size * 0.2, size * 1.0)
    right_wing = rotate_point(-size * 0.2, -size * 1.0)
    
    # Draw wings
    pygame.draw.polygon(win, color, [body_left, left_wing, rotate_point(-size * 0.5, size * 0.3)])
    pygame.draw.polygon(win, color, [body_right, right_wing, rotate_point(-size * 0.5, -size * 0.3)])
    
    # Draw main body
    pygame.draw.polygon(win, color, [head, body_left, body_right])
    
    # Small head circle
    pygame.draw.circle(win, color, (int(head[0]), int(head[1])), int(size * 0.3))

def draw_predator_bird(win, position, velocity, color, size):
    """Draw a larger predator bird (hawk/eagle style)."""
    if velocity.length() > 0.1:
        angle = math.atan2(velocity.y, velocity.x)
    else:
        angle = 0
    
    def rotate_point(x, y):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (
            position.x + x * cos_a - y * sin_a,
            position.y + x * sin_a + y * cos_a
        )
    
    # Predator bird body (more aggressive shape)
    beak = rotate_point(size * 0.9, 0)
    head_top = rotate_point(size * 0.5, -size * 0.2)
    head_bottom = rotate_point(size * 0.5, size * 0.2)
    body_top = rotate_point(-size * 0.2, -size * 0.4)
    body_bottom = rotate_point(-size * 0.2, size * 0.4)
    
    # Larger, more powerful wings
    left_wing = rotate_point(-size * 0.1, size * 1.3)
    right_wing = rotate_point(-size * 0.1, -size * 1.3)
    
    # Tail
    tail_left = rotate_point(-size * 0.8, size * 0.3)
    tail_right = rotate_point(-size * 0.8, -size * 0.3)
    tail_center = rotate_point(-size * 0.6, 0)
    
    # Darker accent for body
    darker_color = tuple(max(0, c - 30) for c in color)
    
    # Draw tail
    pygame.draw.polygon(win, color, [tail_center, tail_left, body_top])
    pygame.draw.polygon(win, color, [tail_center, tail_right, body_bottom])
    
    # Draw wings
    pygame.draw.polygon(win, color, [body_top, left_wing, rotate_point(-size * 0.3, size * 0.7)])
    pygame.draw.polygon(win, color, [body_bottom, right_wing, rotate_point(-size * 0.3, -size * 0.7)])
    
    # Draw body
    pygame.draw.polygon(win, darker_color, [head_top, body_top, body_bottom, head_bottom])
    
    # Draw head and beak
    pygame.draw.polygon(win, color, [beak, head_top, head_bottom])
    head_pos = rotate_point(size * 0.5, 0)
    pygame.draw.circle(win, color, (int(head_pos[0]), int(head_pos[1])), int(size * 0.35))

def draw_boids(win, boids, predators):
    # Realistic bird colors: calm = blue/teal (like small birds), hunted = bright yellow (warning)
    CALM_COLOR = (100, 180, 220)
    HUNTED_COLOR = (255, 220, 50)
    
    # Check which boids are being hunted (if predators have target attribute)
    hunted_boids = []
    for p in predators:
        if hasattr(p, 'target') and p.target is not None:
            hunted_boids.append(p.target)
    
    for b in boids:
        color = HUNTED_COLOR if b in hunted_boids else CALM_COLOR
        draw_bird_shape(win, b.position, b.velocity, color, BOID_SIZE)
        
        hp = max(0, min(100, b.food)) / 100.0
        bar_color = (int(255 * (1 - hp)), int(255 * hp), 0)
        draw_energy_bar(win, b, bar_color, width=14, y_offset=BOID_SIZE + 8)
        
        if checkboxes["arr"].checked:
            arrow = b.position + b.velocity.normalized() * ARROW_LENGTH
            pygame.draw.line(win, (255, 255, 255), (int(b.position.x), int(b.position.y)), (int(arrow.x), int(arrow.y)), 1)
        if checkboxes["rad"].checked:
            pygame.draw.circle(win, (80, 80, 80 ), (int(b.position.x), int(b.position.y)), b.perception_radius, 1)


def draw_predators(win, predators):
    # Predator color: dark red/brown like hawks or eagles
    PREDATOR_COLOR = (140, 60, 40)
    
    for predator in predators:
        # Draw hunting glow/halo when predator can eat
        can_eat = (100 - predator.food) >= PREDATOR_ENERGY_GAIN
        if can_eat:
            # Create a pulsing glow effect using multiple semi-transparent circles
            import time
            pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5  # Oscillates between 0.5 and 1.0
            
            # Create surfaces for transparency
            glow_radius = int(PREDATOR_SIZE * 1.8 * pulse)
            if glow_radius > 0:
                # Outer glow - red/orange halo
                for i in range(3, 0, -1):
                    alpha = int(30 * i / 3 * pulse)
                    radius = glow_radius * (1 + 0.2 * (3 - i))
                    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (200, 50, 30, alpha), (radius, radius), radius)
                    win.blit(s, (int(predator.position.x) - radius, int(predator.position.y) - radius))
        
        draw_predator_bird(win, predator.position, predator.velocity, PREDATOR_COLOR, PREDATOR_SIZE)
        draw_energy_bar(win, predator, (0, 255, 255), width=20, y_offset=PREDATOR_SIZE + 12, height=3)
        
        if checkboxes["arr"].checked:
            arrow = predator.position + predator.velocity.normalized() * ARROW_LENGTH * 1.5
            pygame.draw.line(win, (255, 100, 100), (int(predator.position.x), int(predator.position.y)), (int(arrow.x), int(arrow.y)), 2)
        if checkboxes["rad"].checked:
            real_radius = predator.perception_radius + VISUAL_SIZE_MARGIN
            pygame.draw.circle(win, (80, 80, 80 ), (int(predator.position.x), int(predator.position.y)), real_radius, 1)

def draw_obstacles(win, obstacles):
    import random
    for obstacle in obstacles:
        center_x = int(obstacle.position.x)
        center_y = int(obstacle.position.y)
        radius = obstacle.radius
        
        # Outer tree canopy - dark forest green
        pygame.draw.circle(win, (34, 85, 30), (center_x, center_y), radius)
        
        # Mid-layer foliage - medium green
        pygame.draw.circle(win, (56, 120, 45), (center_x, center_y), int(radius * 0.85))
        
        # Inner foliage - lighter green
        pygame.draw.circle(win, (85, 150, 70), (center_x, center_y), int(radius * 0.65))
        
        # Add foliage texture spots (darker areas for depth)
        random.seed(int(obstacle.position.x + obstacle.position.y))  # Consistent for same tree
        for _ in range(8):
            spot_x = center_x + random.randint(-int(radius * 0.7), int(radius * 0.7))
            spot_y = center_y + random.randint(-int(radius * 0.7), int(radius * 0.7))
            spot_radius = random.randint(3, 7)
            # Check if spot is within the tree
            dist = ((spot_x - center_x)**2 + (spot_y - center_y)**2)**0.5
            if dist < radius:
                pygame.draw.circle(win, (40, 95, 35), (spot_x, spot_y), spot_radius)
        
        # Highlight on top-left for 3D effect
        highlight_x = center_x - int(radius * 0.4)
        highlight_y = center_y - int(radius * 0.4)
        pygame.draw.circle(win, (120, 170, 100), (highlight_x, highlight_y), int(radius * 0.2))

def draw_refuges(win, refuges):
    global refuge_font
    if refuge_font is None:
        refuge_font = pygame.font.SysFont(None, 20)
    for refuge in refuges:
        # Outer cave rock layer - dark grey/brown
        pygame.draw.circle(win, (60, 50, 45), (int(refuge.position.x), int(refuge.position.y)), refuge.radius)
        
        # Middle rocky layer
        pygame.draw.circle(win, (80, 65, 55), (int(refuge.position.x), int(refuge.position.y)), int(refuge.radius * 0.85))
        
        # Inner darker cave opening
        pygame.draw.circle(win, (40, 35, 30), (int(refuge.position.x), int(refuge.position.y)), int(refuge.radius * 0.7))
        
        # Add some rocky texture spots
        import random
        random.seed(int(refuge.position.x + refuge.position.y))  # Consistent seed for same refuge
        for _ in range(6):
            spot_x = int(refuge.position.x) + random.randint(-int(refuge.radius*0.6), int(refuge.radius*0.6))
            spot_y = int(refuge.position.y) + random.randint(-int(refuge.radius*0.6), int(refuge.radius*0.6))
            spot_radius = random.randint(2, 5)
            pygame.draw.circle(win, (50, 42, 38), (spot_x, spot_y), spot_radius)
        
        # Counter text on the refuge
        txt = refuge_font.render(f"{refuge.get_boid_count()}/{refuge.max_capacity}", True, (200, 180, 150))
        rect = txt.get_rect(center=(int(refuge.position.x), int(refuge.position.y)))
        win.blit(txt, rect)

def draw_scene(win, boids, predators, obstacles, refuges, foods):
    win.fill((20, 20, 20))  # Black background
    draw_obstacles(win, obstacles)
    draw_refuges(win, refuges)
    draw_obstacles(win, obstacles)
    draw_food(win, foods)
    draw_predators(win, predators)
    draw_boids(win, boids, predators)
    draw_sliders(win)
    draw_checkboxes(win)
    pygame.display.update()