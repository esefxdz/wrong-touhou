import pygame
import time
from constants import WIDTH, HEIGHT, WHITE, RED, LIGHT_RED

class LevelSystem:
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 10
        self.level_up_text_timer = 0
        self.pending_levels = 0  # unchosen perk level ups
        
        # pause-like system for level up screen
        self.paused = False
        self.last_click_time = 0
        self.click_cooldown = 0.6
        self.font = pygame.font.SysFont(None, 60)
        self.small_font = pygame.font.Font(None, 24)
        
        # level line image
        try:
            self.line_image = pygame.image.load("textures/level_line.png").convert_alpha()
        except:
            self.line_image = pygame.Surface((600, 200), pygame.SRCALPHA)
            self.line_image.fill((80, 80, 160))
        
        # thinner strip - about 30% of screen height
        line_height = int(HEIGHT * 0.30)
        self.line_image = pygame.transform.scale(self.line_image, (WIDTH, line_height))
        
    def add_xp(self, amount):
        self.current_xp += amount
        if self.current_xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.current_xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.level_up_text_timer = 60
        self.pending_levels += 1
        self.paused = True
        
    def check_reopen(self, event):
        """Press L to reopen level up screen if there are pending perks"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            if self.pending_levels > 0 and not self.paused:
                self.paused = True
        
    def draw_xp_bar(self, screen):
        bar_width = 300
        bar_height = 10
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 45  # right underneath health bar
        
        fill_width = (self.current_xp / self.xp_to_next_level) * bar_width
        if fill_width > bar_width:
            fill_width = bar_width

        pygame.draw.rect(screen, (50, 50, 50), (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 200, 255), (x_pos, y_pos, fill_width, bar_height))
        
        lvl_text = self.small_font.render(f"Lvl {self.level}", True, (255, 255, 255))
        screen.blit(lvl_text, (x_pos - 50, y_pos - 4))
        
        if self.level_up_text_timer > 0:
            up_text = self.small_font.render("Level Up!", True, (255, 255, 0))
            screen.blit(up_text, (x_pos + bar_width + 10, y_pos - 4))
            self.level_up_text_timer -= 1
        
        # show pending perks count
        if self.pending_levels > 0:
            pending_text = self.small_font.render(f"({self.pending_levels} pending - press L)", True, (255, 255, 0))
            screen.blit(pending_text, (x_pos + bar_width + 10, y_pos - 4))

    def draw_level_up_screen(self, screen):
        """Draw the level up overlay - called from main loop when paused"""
        if not self.paused:
            return
            
        # transparent dark overlay
        dark_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 100))  # low alpha for transparency  
        screen.blit(dark_surface, (0, 0))
        
        # draw the level_line.png centered vertically
        line_rect = self.line_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(self.line_image, line_rect)
        
        # "Level Up!" title with pending count
        title_str = f"Level Up!  ({self.pending_levels} available)"
        title = self.font.render(title_str, True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, line_rect.top + 15))
        
        # skip button at the bottom of the line image
        skip_button = pygame.Rect(WIDTH // 2 - 100, line_rect.bottom - 60, 200, 45)
        skip_text = self.font.render("Skip", True, WHITE)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        pygame.draw.rect(screen, RED, skip_button)
        if skip_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LIGHT_RED, skip_button)
            current_time = time.time()
            if mouse_click[0] and current_time - self.last_click_time > self.click_cooldown:
                self.last_click_time = current_time
                self.paused = False  # pending_levels stays, player can reopen with L
        
        screen.blit(skip_text, (
            skip_button.centerx - skip_text.get_width() // 2,
            skip_button.centery - skip_text.get_height() // 2
        ))
