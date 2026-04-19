import math
import random
import pygame
from baddies.base_enemy import BaseEnemy

class Flandre(BaseEnemy):
    """Flandre - Rusher enemy that stops for a while, then dashes forward to deal melee damage."""

    SPRITE_PATH = "flandre.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (60, 60)
    MAX_HP = 12
    SPEED = 0  # We use custom dash speed instead
    FIRE_COOLDOWN = 999999  # No projectiles
    
    DROP_XP_RANGE = (5, 9)
    DROP_HP_RANGE = (0, 2)

    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.state = "stop"  # "stop" or "dash"
        self.state_timer = pygame.time.get_ticks()
        self.stop_duration = 1500  # ms she waits before dashing
        self.dash_duration = 600   # ms she spends dashing
        self.dash_speed = 10.0
        self.dash_dx = 0
        self.dash_dy = 0
        self.melee_damage = 1

    def update(self, screen, player, proj_manager):
        if self.defeated:
            return
            
        current_time = pygame.time.get_ticks()
        px, py = player.spaceship_rect.center
        ex, ey = self.lolrect.center
        
        # State machine
        if self.state == "stop":
            if current_time - self.state_timer > self.stop_duration:
                self.state = "dash"
                self.state_timer = current_time
                # Lock in direction toward player at the start of the dash
                dx = px - ex
                dy = py - ey
                distance = math.hypot(dx, dy) or 1
                self.dash_dx = dx / distance
                self.dash_dy = dy / distance
        elif self.state == "dash":
            if current_time - self.state_timer > self.dash_duration:
                self.state = "stop"
                self.state_timer = current_time
            else:
                self.lolrect.x += self.dash_dx * self.dash_speed
                self.lolrect.y += self.dash_dy * self.dash_speed
                
        # Melee contact check (like Yukari)
        if self.lolrect.colliderect(player.spaceship_rect):
            player.take_hit(damage=self.melee_damage)