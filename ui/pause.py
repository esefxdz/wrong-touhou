from tokenize import Whitespace
import pygame
import sys
import os
pygame.init()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

pause_background_image = pygame.image.load("textures/pause_background.jpg")
pause_background_image = pygame.transform.scale(
    pause_background_image,
      (constants.WIDTH, constants.HEIGHT)
      )

#AN IDEA I WILL IMPLEMENT LATER
#screen_size = screen.get_size() #big idea that i will apply to others
#pause_background_image = pygame.image.load("textures/pause_background.jpg")
#pause_background_image = pygame.transform.scale(
#    pause_background_image,
#      screen_size)

class ppause:
    def __init__(self):
        self.paused = False
        self.font = pygame.font.SysFont(None, 60)
        self.pause_background_image = pygame.image.load("textures/pause_background.jpg")
        self.pause_background_image = pygame.transform.scale(
            pause_background_image,
            (constants.WIDTH, constants.HEIGHT)
            )



    def pause_toggle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def blit(self, screen):
        if self.paused:
            screen.blit(self.pause_background_image, (0, 0))
            text = self.font.render("Paused - press esc to resume", True, (constants.WHITE))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 100))