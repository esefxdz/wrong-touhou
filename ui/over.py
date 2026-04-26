import pygame
import sys
import os
import time
import random
from constants import WIDTH, HEIGHT, FONT_LARGE, FONT_MEDIUM

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

from player_files import create_player
from collision_optimizer.projectile_manager import ProjectileManager
from director.wave_director import WaveDirector
from baddies import spawn_enemy

#this is resetting the game after pressing retry i just didnt know where to put it
def reset_game(available_maps, player_class_name="commando"):
    # get fresh map and assets
    m = random.choice(available_maps)
    bg = pygame.image.load(m.MAP_IMAGE)
    bg = pygame.transform.scale(bg, (m.MAP_WIDTH, m.MAP_HEIGHT))
    
    p = create_player(player_class_name, 100, 100, m.MAP_WIDTH, m.MAP_HEIGHT)
    pm = ProjectileManager()
    
    # wave director setup area
    enemies_list = []
    
    # create the director and give it instructions on how to push enemies into our list
    wd = WaveDirector(
        spawn_enemy_callback=lambda type_name: enemies_list.append(spawn_enemy(type_name, p)),
        active_enemies_ref=enemies_list,
        current_map=m
    )
    wd.generate_wave() # force starts wave 1
    
    # reset all map wave timers (legacy maps cleaning)
    for wave in m.ENEMY_WAVES:
        wave.pop("timer", None)
        
    return m, bg, p, enemies_list, pm, wd

class gover:
    def __init__(self):
        self.game_over = False
        self.replay = False
        self.font = pygame.font.SysFont(None, FONT_LARGE)
        self.small_font = pygame.font.SysFont(None, FONT_MEDIUM)
        self.background_image = pygame.image.load("textures/over_background.png")
        self.background_image = pygame.transform.scale(
            self.background_image,
            (WIDTH, HEIGHT)
        )
        self.last_click_time = 0
        self.click_cooldown = 0.6
        self.enemies_killed = 0
        self.damage_dealt = 0
        
    def set_stats(self, enemies, damage):
        self.enemies_killed = enemies
        self.damage_dealt = damage

    def blit(self, screen):
        if self.game_over:
            screen.blit(self.background_image, (0, 0))
            text = self.font.render("Game Over", True, constants.WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))
            
            # Draw stats using the smaller font
            kill_text = self.small_font.render(f"Enemies Defeated: {self.enemies_killed}", True, constants.LIGHT_PINK)
            screen.blit(kill_text, (WIDTH // 2 - kill_text.get_width() // 2, 170))
            
            dmg_text = self.small_font.render(f"Damage Dealt: {self.damage_dealt}", True, constants.LIGHT_PINK)
            screen.blit(dmg_text, (WIDTH // 2 - dmg_text.get_width() // 2, 220))

    def buttons(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        # Position buttons below the stats
        replay_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50)
        quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
        
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
