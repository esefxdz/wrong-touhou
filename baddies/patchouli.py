import math
import pygame
import os
from baddies.base_enemy import BaseEnemy
from constants import PURPLE, LIGHT_PURPLE

class Patchouli(BaseEnemy):
    """Patchouli - Sniper that locks on with a laser before firing a fast purple beam."""

    #------------------------------------------
    # sniper config / her stats and laser colors
    #------------------------------------------
    SPRITE_PATH = "patchouli.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 3
    SPEED = 1
    FIRE_COOLDOWN = 3000
    FIRE_SPEED = 400
    FIRE_COLOR = PURPLE          # purple beam
    FIRE_ON_SCREEN_ONLY = True          # won't fire off-screen
    SNIPER_LASER_TRACK_COLOR = LIGHT_PURPLE  # thin tracking laser color
    POST_FIRE_DURATION = 300            # ms the thick beam lingers after firing

    #------------------------------------------
    # drop table / sniper, high threat so decent reward
    #------------------------------------------
    DROP_XP_RANGE = (3, 6)   # 3-6 XP orbs per kill
    DROP_HP_RANGE  = (0, 1)  # 0-1 HP orb

    def __init__(self, player_ref):
        super().__init__(player_ref)
        
        # laser tracking state
        self._locked_angle = None
        self._draw_laser = False
        self._post_fire_angle = None
        self._post_fire_time = 0

    #------------------------------------------
    # sniper fire override / lock on and shoot
    #------------------------------------------
    def fire(self, proj_manager, cam_offset=(0, 0)):
        if self.defeated:
            return
        
        # stall cooldown timer while off screen so she doesn't queue up shots
        current_time = pygame.time.get_ticks()
        time_since = current_time - self.last_fire_time
        if self.FIRE_ON_SCREEN_ONLY and not self._is_on_screen(cam_offset):
            if time_since > self.FIRE_COOLDOWN - 1000:
                self.last_fire_time = current_time - (self.FIRE_COOLDOWN - 1000)
            self._draw_laser = False
            return

        # always track player with laser
        px, py = self.player.spaceship_rect.center
        dx = px - self.lolrect.centerx
        dy = py - self.lolrect.centery
        self._locked_angle = math.atan2(dy, dx)
        self._draw_laser = True

        # fire when cooldown expires
        if time_since > self.FIRE_COOLDOWN:
            self._post_fire_angle = self._locked_angle
            self._post_fire_time = current_time
            fire_dx = math.cos(self._locked_angle)
            fire_dy = math.sin(self._locked_angle)
            proj_manager.spawn(
                self.lolrect.centerx, self.lolrect.centery,
                fire_dx, fire_dy, self.fire_speed,
                radius=8, color=self.FIRE_COLOR, type_id=0, owner=1, angle=self._locked_angle
            )
            self.last_fire_time = current_time

    #------------------------------------------
    # sniper draw override / laser visuals on top of sprite
    #------------------------------------------
    def draw(self, screen, cam_offset):
        if self.defeated:
            return

        current_time = pygame.time.get_ticks()
        sx = self.lolrect.centerx - cam_offset[0]
        sy = self.lolrect.centery - cam_offset[1]

        # thick fading beam after the shot
        if self._post_fire_angle is not None:
            age = current_time - self._post_fire_time
            if age < self.POST_FIRE_DURATION:
                t = 1.0 - (age / self.POST_FIRE_DURATION)
                thickness = max(1, int(24 * t))
                r, g, b = self.FIRE_COLOR
                ex = sx + math.cos(self._post_fire_angle) * 2000
                ey = sy + math.sin(self._post_fire_angle) * 2000
                pygame.draw.line(screen, (r, g, b), (int(sx), int(sy)), (int(ex), int(ey)), thickness)
            else:
                self._post_fire_angle = None

        # thin tracking laser while locking on
        if self._draw_laser and self._locked_angle is not None:
            ex = sx + math.cos(self._locked_angle) * 2000
            ey = sy + math.sin(self._locked_angle) * 2000
            pygame.draw.line(screen, self.SNIPER_LASER_TRACK_COLOR, (int(sx), int(sy)), (int(ex), int(ey)), 1)

        # draw sprite and healthbar from base
        super().draw(screen, cam_offset)
