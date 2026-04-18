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
    
    #------------------------------------------
    # common enemy stats / the basic stuff
    # target: @everyone
    #------------------------------------------
    SPRITE_PATH = None      # path to sprite image relative to baddies folder
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 2
    SPEED = 1.5
    FIRE_COOLDOWN = 1000    # ms between shots
    FIRE_SPEED = 3          # bullet travel speed
    FIRE_COLOR = (255, 0, 0)

    #------------------------------------------
    # game initialization area / hooking up the basics
    # target: @everyone
    #------------------------------------------
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
        self.fire_speed = self.FIRE_SPEED
            
        # spawn
        self.spawn_outside_screen()
    
    #------------------------------------------
    # map spawning stuff / dropping them outside the screen
    # target: @everyone
    #------------------------------------------
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
    
    def _is_on_screen(self, cam_offset):
        sx = self.lolrect.centerx - cam_offset[0]
        sy = self.lolrect.centery - cam_offset[1]
        return -50 <= sx <= constants.WIDTH + 50 and -50 <= sy <= constants.HEIGHT + 50

    #------------------------------------------
    # firing system / single bullet aimed at player
    # target: @everyone
    #------------------------------------------
    def fire(self, proj_manager, cam_offset=(0, 0)):
        if self.defeated:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > self.fire_cooldown:
            self.last_fire_time = current_time
            enemy_x, enemy_y = self.lolrect.center
            player_x, player_y = self.player.spaceship_rect.center
            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy) or 1
            angle = math.atan2(dy, dx)
            proj_manager.spawn(
                enemy_x, enemy_y,
                dx / distance, dy / distance, self.fire_speed,
                radius=5, color=self.FIRE_COLOR, type_id=0, owner=1, angle=angle
            )

    #------------------------------------------
    # health and movement / taking damage and chasing player
    # target: @everyone
    #------------------------------------------
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
    
    #------------------------------------------
    # main update loop / running all the math
    # target: @everyone
    #------------------------------------------
    def update(self, screen, player, proj_manager):
        if not self.defeated:
            self.move_toward_player()
            cam_offset = player.get_camera_offset()
            self.fire(proj_manager, cam_offset)

    #------------------------------------------
    # master drawing area / slapping all their sprites on screen
    # target: @everyone
    #------------------------------------------
    def draw(self, screen, cam_offset):
        if self.defeated:
            return

        # draw sprite
        image_rect = self.image.get_rect(center=self.lolrect.center)
        screen.blit(self.image, (image_rect.x - cam_offset[0], image_rect.y - cam_offset[1]))

        #------------------------------------------
        # little healthbars on top of their heads
        # target: @everyone
        #------------------------------------------
        current_hp = self.max_hp - self.hit_count
        bar_w = min(self.lolrect.width, 50)
        bar_h = 6
        hp_ratio = max(0.0, current_hp / self.max_hp)
        fill_w = int(bar_w * hp_ratio)
        
        bx = self.lolrect.centerx - cam_offset[0] - (bar_w // 2)
        by = self.lolrect.top - cam_offset[1] - 15
        
        # red background then green health fill
        pygame.draw.rect(screen, (255, 0, 0), (bx, by, bar_w, bar_h))
        if fill_w > 0:
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, fill_w, bar_h))