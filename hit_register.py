import pygame
from baddies.enemy import rumia
from player import spaceship

def player_hit(bullets, lolrect):
    for bullet in bullets:
        if bullet.colliderect(lolrect):
            print("hit")

def boss_hit(fires, spaceship_rect):
    for fire in fires:
        if fire.colliderect(spaceship_rect):
            print("Player hit")
