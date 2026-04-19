import math
import random
import pygame
from baddies.base_enemy import BaseEnemy
from constants import LIGHT_RED, YELLOW, DARK_GRAY

class Tewi(BaseEnemy):
    """Tewi - Mortar enemy that stays at a distance and drops exploding mortars from the sky."""

    SPRITE_PATH = "tewi.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 8
    SPEED = 1.2
    FIRE_COOLDOWN = 3000  # How often she launches a mortar
    
    DROP_XP_RANGE = (4, 7)
    DROP_HP_RANGE = (0, 1)

    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.mortars = []  # Tracks active mortars: {tx, ty, spawn_time, explode_time, exploded}
        self.maintain_distance = 500  # Distance she wants to stay away from the player
        self.explosion_radius = 120

    def update(self, screen, player, proj_manager):
        if self.defeated:
            return
            
        current_time = pygame.time.get_ticks()
        px, py = player.spaceship_rect.center
        ex, ey = self.lolrect.center
        
        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)
        
        # Movement logic: reposition to stay at maintain_distance
        if dist > 0:
            if dist > self.maintain_distance + 50:
                self.lolrect.x += (dx / dist) * self.SPEED
                self.lolrect.y += (dy / dist) * self.SPEED
            elif dist < self.maintain_distance - 50:
                self.lolrect.x -= (dx / dist) * self.SPEED
                self.lolrect.y -= (dy / dist) * self.SPEED

        # Firing logic
        if current_time - self.last_fire_time > self.fire_cooldown:
            self.last_fire_time = current_time
            # Drop a mortar where the player is currently standing
            self.mortars.append({
                "tx": px,
                "ty": py,
                "spawn_time": current_time,
                "explode_time": current_time + 1500,  # 1.5 second warning shadow
                "exploded": False
            })

        # Update active mortars & check explosions
        for m in self.mortars:
            if not m["exploded"] and current_time >= m["explode_time"]:
                m["exploded"] = True
                mx, my = m["tx"], m["ty"]
                # Check for damage radius
                m_dist = math.hypot(px - mx, py - my)
                # Player gets hit if they are inside the explosion radius
                if m_dist < self.explosion_radius + player.hitbox_radius:
                    player.take_hit()
                    
        # Remove mortars that finished their explosion linger duration (e.g. 200ms)
        self.mortars = [m for m in self.mortars if not (m["exploded"] and current_time > m["explode_time"] + 200)]

    def draw(self, screen, cam_offset):
        if self.defeated:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Draw mortars (drawn before sprite so they are underneath the enemy but on top of map)
        for m in self.mortars:
            sx = m["tx"] - cam_offset[0]
            sy = m["ty"] - cam_offset[1]
            
            if m["exploded"]:
                # Draw the impact explosion briefly
                pygame.draw.circle(screen, LIGHT_RED, (int(sx), int(sy)), self.explosion_radius)
                pygame.draw.circle(screen, YELLOW, (int(sx), int(sy)), int(self.explosion_radius * 0.8))
            else:
                # Calculate progress from 0.0 to 1.0
                progress = (current_time - m["spawn_time"]) / (m["explode_time"] - m["spawn_time"])
                progress = max(0.0, min(1.0, progress))
                
                # Shadow growing and darkening
                current_radius = int(self.explosion_radius * progress)
                alpha = int(180 * progress)
                shadow_surf = pygame.Surface((self.explosion_radius * 2, self.explosion_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surf, (150, 0, 0, alpha), (self.explosion_radius, self.explosion_radius), current_radius)
                # Danger outline
                pygame.draw.circle(shadow_surf, (255, 0, 0, alpha + 50), (self.explosion_radius, self.explosion_radius), self.explosion_radius, max(1, int(4 * progress)))
                screen.blit(shadow_surf, (sx - self.explosion_radius, sy - self.explosion_radius))
                
                # The falling projectile (drawn high above falling down)
                fall_height = 800 * (1.0 - progress)
                pygame.draw.circle(screen, DARK_GRAY, (int(sx), int(sy - fall_height)), max(5, int(25 * progress)))

        # Draw the enemy sprite and health normally
        super().draw(screen, cam_offset)