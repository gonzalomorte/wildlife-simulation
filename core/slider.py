import pygame

class Slider:
    HITBOX_HEIGHT = 12
    CURSOR_WIDTH = 10
    CURSOR_HEIGHT = 16
    
    def __init__(self, x, y, width, min_val, max_val, start_val):
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_val
        self.max_value = max_val
        self.current_value = start_val
        self.active = False   # Replaces active_slider


    def update(self, mouse_pos, mouse_pressed):
        # 2. If dragging this slider
        if self.active and left_click:
            relative = (mouseX - self.x) / self.width
            relative = max(0, min(1, relative))   # clamp 0..1
            self.value = self.min_value + relative * (self.max_value - self.min_value)

        # 3. Release
        if not left_click:
            self.active = False

            