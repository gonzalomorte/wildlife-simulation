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

    def draw(self, win):
        # Draw square
        pygame.draw.rect(win, (255,255,255), self.rect, 2)

        # Fill if checked
        if self.checked:
            pygame.draw.rect(win, (255,255,255), self.rect.inflate(-6, -6))

        # Draw text
        label = self.font.render(self.text, True, (255,255,255))
        win.blit(label, (self.x + self.size + 10, self.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
