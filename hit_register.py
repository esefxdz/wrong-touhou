import pygame
from baddies.enemy import rumia
from player import spaceship
boss = rumia

def player_hit(bullets, lolrect, take_hit):
    for bullet in bullets:
        if bullet.colliderect(lolrect):
            take_hit()
            

def boss_hit(fires, spaceship_rect):
    for fire in fires:
        if fire.colliderect(spaceship_rect):
            print("Player hit")
