import pygame

class Checkbox:
    def __init__(self, x, y, text, checked=False):
        self.x = x
        self.y = y
        self.text = text
        self.checked = checked

        self.size = 20
        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.font = pygame.font.SysFont(None, 24)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
