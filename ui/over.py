import pygame
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

class gover:
    def __init__(self):
        self.game_over = False
        self.font = pygame.font.SysFont(None, 60)
        self.background_image = pygame.image.load("textures/over_background.png")
        self.background_image = pygame.transform.scale(
            self.background_image,
            (constants.WIDTH, constants.HEIGHT)
        )
        self.last_click_time = 0
        self.click_cooldown = 0.6
        self.replay = False
        self.enemies_killed = 0
        self.damage_dealt = 0
        
    def set_stats(self, enemies, damage):
        self.enemies_killed = enemies
        self.damage_dealt = damage

    def blit(self, screen):
        if self.game_over:
            screen.blit(self.background_image, (0, 0))
            text = self.font.render("Game Over", True, constants.WHITE)
            screen.blit(text, (constants.WIDTH // 2 - text.get_width() // 2, 100))
            
            stats_font = pygame.font.SysFont(None, 40)
            kill_text = stats_font.render(f"Enemies Killed: {self.enemies_killed}", True, constants.WHITE)
            dmg_text = stats_font.render(f"Damage Dealt: {self.damage_dealt}", True, constants.WHITE)
            
            screen.blit(kill_text, (constants.WIDTH // 2 - kill_text.get_width() // 2, 170))
            screen.blit(dmg_text, (constants.WIDTH // 2 - dmg_text.get_width() // 2, 220))

    def buttons(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        replay_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 - 30, 200, 50)
        quit_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 + 50, 200, 50)
        
        replay_text = self.font.render("Replay", True, constants.WHITE)
        quit_text = self.font.render("Quit", True, constants.WHITE)

        pygame.draw.rect(screen, constants.GREEN, replay_button)
        if replay_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_GREEN, replay_button)
            current_time = time.time()
            if mouse_click[0] and current_time - self.last_click_time > self.click_cooldown:
                self.last_click_time = current_time
                self.replay = True
                self.game_over = False
        
        pygame.draw.rect(screen, constants.RED, quit_button)
        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_RED, quit_button)
            if mouse_click[0]:
                pygame.quit()
                sys.exit()

        screen.blit(replay_text, (
            replay_button.centerx - replay_text.get_width() // 2,
            replay_button.centery - replay_text.get_height() // 2
        ))
        screen.blit(quit_text, (
            quit_button.centerx - quit_text.get_width() // 2,
            quit_button.centery - quit_text.get_height() // 2
        ))
