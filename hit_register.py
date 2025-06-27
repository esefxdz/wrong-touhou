import pygame
from baddies.enemy import rumia
from player import spaceship
boss = rumia

def player_hit(bullets, target_rect, take_hit):
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet["pos"][0], bullet["pos"][1], 5, 5)
        if bullet_rect.colliderect(target_rect):
            take_hit()

            

def boss_hit(fires, spaceship_rect):
    for fire in fires:
        fire_rect = pygame.Rect(fire["pos"][0], fire["pos"][1], 5, 5)
