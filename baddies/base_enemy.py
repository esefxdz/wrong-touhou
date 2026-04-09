import sys
import os
import pygame
import random
import math
pygame.mixer.init()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

class BaseEnemy:
    """Base class for all enemies. Subclass this and override the config to create new enemies."""
    
    # === OVERRIDE THESE IN SUBCLASSES ===
    SPRITE_PATH = None      # path to sprite image relative to baddies folder
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 2
    SPEED = 1.5
    FIRE_COOLDOWN = 1000    # ms between shots
    FIRE_SPEED = 3          # bullet travel speed
    FIRE_COLOR = (255, 0, 0)
    
    def __init__(self, player_ref):
        self.player = player_ref
        
        # load sprite
        if self.SPRITE_PATH:
            image_path = os.path.join(os.path.dirname(__file__), self.SPRITE_PATH)
            self.image = pygame.image.load(image_path)
        else:
            self.image = pygame.Surface(self.SPRITE_SIZE)
            self.image.fill((255, 0, 255))  # magenta = missing texture
        self.image = pygame.transform.scale(self.image, self.SPRITE_SIZE)
        
        # hitbox
        self.lolrect = pygame.Rect(0, 0, *self.HITBOX_SIZE)
        
        # health
        self.max_hp = self.MAX_HP
        self.hit_count = 0
        self.defeated = False
        
        # shooting
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = self.FIRE_COOLDOWN
        self.fires = []
        self.fire_speed = self.FIRE_SPEED
        
        # spawn
        self.spawn_outside_screen()
    
    def spawn_outside_screen(self):
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery
        margin = 200
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = player_x + random.randint(-constants.WIDTH // 2, constants.WIDTH // 2)
            y = player_y - constants.HEIGHT // 2 - margin
        elif side == 'bottom':
            x = player_x + random.randint(-constants.WIDTH // 2, constants.WIDTH // 2)
            y = player_y + constants.HEIGHT // 2 + margin
        elif side == 'left':
            x = player_x - constants.WIDTH // 2 - margin
            y = player_y + random.randint(-constants.HEIGHT // 2, constants.HEIGHT // 2)
        else:
            x = player_x + constants.WIDTH // 2 + margin
            y = player_y + random.randint(-constants.HEIGHT // 2, constants.HEIGHT // 2)
        x = max(0, min(x, self.player.map_w))
        y = max(0, min(y, self.player.map_h))
        self.lolrect.topleft = (x, y)
    
    def fire(self):
        if self.defeated:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > self.fire_cooldown:
            self.last_fire_time = current_time
            
            enemy_x, enemy_y = self.lolrect.center
            player_x, player_y = self.player.spaceship_rect.center
            
            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1
            
            direction = (dx / distance, dy / distance)
            self.fires.append({
                "pos": [enemy_x, enemy_y],
                "dir": direction
            })
    
    def update_fire(self, screen):
        new_fires = []
        for f in self.fires:
            f["pos"][0] += f["dir"][0] * self.fire_speed
            f["pos"][1] += f["dir"][1] * self.fire_speed
            if 0 <= f["pos"][0] <= self.player.map_w and 0 <= f["pos"][1] <= self.player.map_h:
                new_fires.append(f)
        self.fires = new_fires
    
    def take_hit(self):
        if not self.defeated:
            self.hit_count += 1
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
            if self.hit_count >= self.max_hp:
                self.defeated = True
                self.player.enemies_killed += 1
                pygame.mixer.Sound(os.path.join("sounds", "killsound.wav")).play()
    
    def move_toward_player(self):
        enemy_x = self.lolrect.centerx
        enemy_y = self.lolrect.centery
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery
        
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        
        dx = dx / distance
        dy = dy / distance
        self.lolrect.x += dx * self.SPEED
        self.lolrect.y += dy * self.SPEED
    
    def update(self, screen):
        if not self.defeated:
            self.move_toward_player()
        self.update_fire(screen)
    
    def draw(self, screen, cam_offset):
        if not self.defeated:
            image_rect = self.image.get_rect(center=self.lolrect.center)
            screen_x = image_rect.x - cam_offset[0]
            screen_y = image_rect.y - cam_offset[1]
            screen.blit(self.image, (screen_x, screen_y))
        for f in self.fires:
            screen_x = int(f["pos"][0]) - cam_offset[0]
            screen_y = int(f["pos"][1]) - cam_offset[1]
            pygame.draw.circle(screen, self.FIRE_COLOR, (screen_x, screen_y), 5)
