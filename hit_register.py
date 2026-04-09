import pygame
from baddies.enemy import rumia
from player_files.player import spaceship
boss = rumia

def player_hit(player, target_rect, take_hit):
    for bullet in reversed(player.bullets):
        # player bullets are 20x40, center the hitbox on the bullet pos
        bullet_rect = pygame.Rect(0, 0, 20, 40)
        bullet_rect.center = (int(bullet["pos"][0]), int(bullet["pos"][1]))
        
        if bullet_rect.colliderect(target_rect):
            take_hit()
            player.damage_dealt += 1
            player.level_system.add_xp(1)
            player.bullets.remove(bullet)

def boss_hit(fires, spaceship_rect, take_hit):
    for fire in reversed(fires):
        # enemy fires are circles with radius 5, so 10x10 hitbox
        fire_rect = pygame.Rect(0, 0, 10, 10)
        fire_rect.center = (int(fire["pos"][0]), int(fire["pos"][1]))
        
        if fire_rect.colliderect(spaceship_rect):
            take_hit()
            fires.remove(fire)
