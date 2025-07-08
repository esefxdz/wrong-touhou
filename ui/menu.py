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
            self.menu_button(screen)
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

    def menu_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        play_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 - 50, 200, 50)
        quit_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 + 25, 200, 50)
        #its better than getting normal coordinates because this one doesnt shit itself with different resolutions 
        play_text = self.font.render("Play", True, constants.WHITE)
        quit_text = self.font.render("Quit", True, constants.WHITE)

        pygame.draw.rect(screen, (constants.GREEN), play_button)
        if play_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_GREEN, play_button)
            if mouse_click[0]:
                self.menu = False
        
        pygame.draw.rect(screen, constants.RED, quit_button)
        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_RED, quit_button)
            if mouse_click[0]:
                pygame.quit()
                sys.exit()

        screen.blit(play_text, (play_button.centerx - play_text.get_width() // 2, play_button.centery - play_text.get_height() // 2))
        screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2)) 
        pygame.display.update()          