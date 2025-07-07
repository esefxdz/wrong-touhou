import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

menu_background_image = pygame.image.load("textures/menu_background.jpg")
menu_background_image = pygame.transform.scale(
    menu_background_image,
      (constants.WIDTH, constants.HEIGHT)
      )

class mmenu:
    def __init__(self):
        self.menu = True
        self.font = pygame.font.SysFont(None, 60)
        self.pause_background_image = pygame.image.load("textures/menu_background.jpg")
        self.pause_background_image = pygame.transform.scale(
            menu_background_image,
            (constants.WIDTH, constants.HEIGHT)
            )
        
    def run(self, screen, clock):
        print("clock achieved")
        while self.menu:
            screen.blit(menu_background_image, (0, 0))
            text = self.font.render("WELCOME TO MY GAME", True, (constants.WHITE))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 100))
            self.handle_events()
            pygame.display.flip()
            clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        koys = pygame.key.get_pressed()
        if koys[pygame.K_RETURN]:
            self.menu = False
        if self.menu:
            if koys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()