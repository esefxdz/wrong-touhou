import pygame
from constants import WIDTH

class LevelSystem:
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 10
        self.level_up_text_timer = 0
        
    def add_xp(self, amount):
        self.current_xp += amount
        if self.current_xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.current_xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.level_up_text_timer = 60 # Show text for 1 second at 60 fps
        
    def draw_xp_bar(self, screen):
        bar_width = 300
        bar_height = 10
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 45 # right underneath health bar
        
        fill_width = (self.current_xp / self.xp_to_next_level) * bar_width
        if fill_width > bar_width: fill_width = bar_width

        pygame.draw.rect(screen, (50, 50, 50), (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 200, 255), (x_pos, y_pos, fill_width, bar_height))
        
        font = pygame.font.Font(None, 24)
        lvl_text = font.render(f"Lvl {self.level}", True, (255, 255, 255))
        screen.blit(lvl_text, (x_pos - 50, y_pos - 4))
        
        if self.level_up_text_timer > 0:
            up_text = font.render("Level Up!", True, (255, 255, 0))
            screen.blit(up_text, (x_pos + bar_width + 10, y_pos - 4))
            self.level_up_text_timer -= 1
