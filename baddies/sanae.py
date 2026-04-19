import math
import random
import pygame
from baddies.base_enemy import BaseEnemy
from constants import GREEN, LIGHT_GREEN

class Sanae(BaseEnemy):
    """Sanae - Healer enemy that avoids the player and restores HP to other enemies."""

    SPRITE_PATH = "sanae.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 8
    SPEED = 1.3
    FIRE_COOLDOWN = 3000  # How often she is allowed to heal someone
    
    DROP_XP_RANGE = (4, 8)
    DROP_HP_RANGE = (0, 2)

    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.maintain_distance = 700  # She will run away to this distance
        self.heal_target_position = None
        self.heal_timer = 0
        self.heal_visual_duration = 300  # How long the healing beam displays
        
    def move_away_from_player(self, player):
        px, py = player.spaceship_rect.center
        ex, ey = self.lolrect.center
        
        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)
        
        if dist == 0:
            return
            
        # Instead of moving toward, run away backwards!
        if dist < self.maintain_distance:
            self.lolrect.x -= (dx / dist) * self.SPEED
            self.lolrect.y -= (dy / dist) * self.SPEED
            
        # Since Sanae's goal is to survive, she will try not to leave the map limits
        self.lolrect.x = max(0, min(self.lolrect.x, self.player.map_w - self.lolrect.width))
        self.lolrect.y = max(0, min(self.lolrect.y, self.player.map_h - self.lolrect.height))

    def update(self, screen, player, proj_manager):
        if self.defeated:
            return
            
        current_time = pygame.time.get_ticks()
        
        self.move_away_from_player(player)
        
        # Healing Logic
        if current_time - self.last_fire_time > self.fire_cooldown:
            # Look for a wounded ally in the enemies list we hooked up over in main.py
            if hasattr(self, 'active_enemies_list'):
                best_target = None
                best_dist = float('inf')
                ex, ey = self.lolrect.center
                
                for friend in self.active_enemies_list:
                    # Don't heal herself or dead enemies
                    if friend is self or friend.defeated:
                        continue
                        
                    # Target only those missing HP (hit_count > 0 means they took damage)
                    if friend.hit_count > 0:
                        fx, fy = friend.lolrect.center
                        dist = math.hypot(fx - ex, fy - ey)
                        # Can only reach targets within 900px
                        if dist < 900 and dist < best_dist:
                            best_dist = dist
                            best_target = friend
                            
                if best_target:
                    # Found someone to rescue! 
                    # Decreasing hit_count grants them their HP back.
                    best_target.hit_count = max(0, best_target.hit_count - 2)
                    self.heal_target_position = best_target.lolrect.center
                    self.heal_timer = current_time
                    self.last_fire_time = current_time
                else:
                    # No one to heal right now, stall the cooldown slightly so she checks again quickly (in 0.5s instead of 3s)
                    self.last_fire_time = current_time - (self.FIRE_COOLDOWN - 500)

    def draw(self, screen, cam_offset):
        if self.defeated:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Visual healing beam underneath her sprite
        if self.heal_target_position:
            age = current_time - self.heal_timer
            if age < self.heal_visual_duration:
                # Thins out as it fades
                thickness = max(1, 8 - (age // 40))
                
                sx = self.lolrect.centerx - cam_offset[0]
                sy = self.lolrect.centery - cam_offset[1]
                tx = self.heal_target_position[0] - cam_offset[0]
                ty = self.heal_target_position[1] - cam_offset[1]
                
                # Green healing beam
                pygame.draw.line(screen, GREEN, (int(sx), int(sy)), (int(tx), int(ty)), thickness)
                # Little burst ring around the healed target
                pygame.draw.circle(screen, LIGHT_GREEN, (int(tx), int(ty)), int((age / self.heal_visual_duration) * 40), max(1, thickness))
            else:
                self.heal_target_position = None
                
        # Ensure super() draws her sprite and HP bar on top
        super().draw(screen, cam_offset)