import math
import pygame
from baddies.base_enemy import BaseEnemy
from constants import CYAN

class Cirno(BaseEnemy):
    """Cirno - Shotgunner enemy that fires blue projectiles in a spread."""

    #------------------------------------------
    # shotgun config / her stats and spread settings
    #------------------------------------------
    SPRITE_PATH = "cirno.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 4              # tougher than rumia
    SPEED = 1.0             # slightly slower
    FIRE_COOLDOWN = 1500    # shoots slower
    FIRE_SPEED = 2          # slower bullets
    FIRE_COLOR = CYAN  # cyan / blue
    FIRE_COUNT = 5          # pellets per shot
    FIRE_SPREAD_ANGLE = 45  # cone width in degrees

    #------------------------------------------
    # drop table / shotgunner, medium difficulty
    #------------------------------------------
    DROP_XP_RANGE = (2, 5)   # 2-5 XP orbs per kill
    DROP_HP_RANGE  = (0, 1)  # 0-1 HP orb (small chance)

    #------------------------------------------
    # shotgun fire override / blasting a spread at the player
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
            base_angle = math.atan2(dy, dx)

            # spread each pellet evenly across the cone
            for i in range(self.FIRE_COUNT):
                fraction = i / (self.FIRE_COUNT - 1)
                angle_offset = math.radians(self.FIRE_SPREAD_ANGLE * (fraction - 0.5))
                fire_angle = base_angle + angle_offset
                proj_manager.spawn(
                    enemy_x, enemy_y,
                    math.cos(fire_angle), math.sin(fire_angle), self.fire_speed,
                    radius=5, color=self.FIRE_COLOR, type_id=0, owner=1, angle=fire_angle
                )
