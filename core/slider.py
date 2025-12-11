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


    def update(self, mouseX):
        """Update this slider's value if it's being dragged."""
        relative_pos = (mouseX - self.x) / self.width  # Normalizes the mouse position from the starting point (how far is from the left edge)
        relative_pos = max(0, min(1, relative_pos))  # relative_pos = a value between 0 and 1 (if relative_pos<0 -> 0; if relative_pos>1 -> 1; if 0<=relative_pos<=1 -> relative_pos). Then cannot be lower than 0 or higher than 1
        self.current_value = self.min_value + relative_pos * (self.max_value - self.min_value)
    

            