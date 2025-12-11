import pygame

class Slider:
    SLIDER_HITBOX_HEIGHT = 12
    SLIDER_CURSOR_WIDTH = 10
    SLIDER_CURSOR_HEIGHT = 16
    
    def __init__(self, x, y, width, min_val, max_val, start_val):
        self.x = x
        self.y = y
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.active = False   # Replaces active_slider


    def update(self, mouse_pos, mouse_pressed):
        mouseX, mouseY = mouse_pos
        left_click = mouse_pressed[0]

        # 1. If user clicks and slider is not active → check if slider is clicked
        if left_click and not self.active:
            inside_x = self.x <= mouseX <= self.x + self.width
            inside_y = self.y <= mouseY <= self.y + Slider.HITBOX_HEIGHT

            if inside_x and inside_y:
                self.active = True

        # 2. If dragging this slider
        if self.active and left_click:
            relative = (mouseX - self.x) / self.width
            relative = max(0, min(1, relative))   # clamp 0..1
            self.value = self.min_val + relative * (self.max_val - self.min_val)

        # 3. Release
        if not left_click:
            self.active = False