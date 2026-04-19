import pygame
import sys
import os
import time
from constants import WIDTH, HEIGHT, FONT_MEDIUM, DARK_GRAY, BLACK, GREEN, LIGHT_GREEN, WHITE

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class ShopMenu:
    def __init__(self):
        # shop state and fading settings
        self.active = False
        self.fade_alpha = 0
        self.fade_speed = 5
        self.font = pygame.font.SysFont(None, FONT_MEDIUM)
        
        # loading the background picture
        try:
            self.background_image = pygame.image.load("ui/shop_menu/shop_background.png").convert_alpha()
            self.background_image = pygame.transform.scale(
                self.background_image,
                (WIDTH, HEIGHT)
            )
        except Exception:
            self.background_image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.background_image.fill((*DARK_GRAY, 255))
            
        # skip button cooldowns
        self.last_click_time = 0
        self.click_cooldown = 0.5
        
        # setup the fade surface
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.fade_surface.fill((0, 0, 0, 0))

    def trigger(self):
        # starts the shop sequence
        self.active = True
        self.fade_alpha = 0
        self.last_click_time = time.time()

    def draw(self, screen):
        # skip drawing if we arent active
        if not self.active:
            return
            
        # fade in effect logic
        if self.fade_alpha < 255:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha > 255:
                self.fade_alpha = 255
            
            # create copied background and overlay elements
            bg_copy = self.background_image.copy()
            bg_copy.set_alpha(self.fade_alpha)
            
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(self.fade_alpha)
            
            # blit the darkening overlay first then the shop background
            screen.blit(overlay, (0, 0))
            screen.blit(bg_copy, (0, 0))
        else:
            # draw full picture and buttons when completely faded in
            screen.blit(self.background_image, (0, 0))
            self.buttons(screen)
            
    def buttons(self, screen):
        # checking mouse input
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        # skip button visuals
        skip_button = pygame.Rect(WIDTH - 150, HEIGHT - 80, 130, 50)
        skip_text = self.font.render("Skip", True, WHITE)
        
        # hover effects and click logic
        pygame.draw.rect(screen, GREEN, skip_button)
        if skip_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LIGHT_GREEN, skip_button)
            current_time = time.time()
            if mouse_click[0] and current_time - self.last_click_time > self.click_cooldown:
                self.last_click_time = current_time
                self.active = False
                
        # pasting the text on top
        screen.blit(skip_text, (
            skip_button.centerx - skip_text.get_width() // 2,
            skip_button.centery - skip_text.get_height() // 2
        ))
