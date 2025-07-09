from tokenize import Whitespace
import pygame
import sys
import os
import time
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
        self.menu = False
        self.font = pygame.font.SysFont(None, 60)
        self.pause_background_image = pygame.image.load("textures/pause_background.jpg")
        self.pause_background_image = pygame.transform.scale(
            pause_background_image,
            (constants.WIDTH, constants.HEIGHT)
            )
        #cooldown between clicks because im too dumb to implement event driven click system
        self.last_click_time = 0
        self.click_cooldown = 0.6



    def pause_toggle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    def blit(self, screen):
        if self.paused:
            screen.blit(self.pause_background_image, (0, 0))
            text = self.font.render("Paused - press esc to resume", True, (constants.WHITE))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 100))

    def pause_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        resume_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 - 90, 200, 50)
        main_menu_button = pygame.Rect(constants.WIDTH // 2 - 112, constants.HEIGHT // 2 - 30, 225, 50)
        quit_button = pygame.Rect(constants.WIDTH // 2 - 100, constants.HEIGHT // 2 + 25, 200, 50)
        #its better than getting normal coordinates because this one doesnt shit itself with different resolutions 
        resume_text = self.font.render("Resume", True, constants.WHITE)
        main_menu_text = self.font.render("Main Menu", True, constants.WHITE)
        quit_text = self.font.render("Quit", True, constants.WHITE)

        pygame.draw.rect(screen, (constants.GREEN), resume_button)
        if resume_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_GREEN, resume_button)
            if mouse_click[0]:
                self.paused = False
        
        pygame.draw.rect(screen, constants.RED, quit_button)
        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_RED, quit_button)
            if mouse_click[0]:
                pygame.quit()
                sys.exit()

        pygame.draw.rect(screen, constants.GREEN, main_menu_button)
        if main_menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, constants.LIGHT_GREEN, main_menu_button)
            current_time = time.time()
            if mouse_click[0] and current_time - self.last_click_time > self.click_cooldown: #puts the cooldown
                self.last_click_time = current_time # resets the counter
                self.paused = False
                self.menu = True
        
        screen.blit(resume_text, (
        resume_button.centerx - resume_text.get_width() // 2,
        resume_button.centery - resume_text.get_height() // 2
    ))
        screen.blit(quit_text, (
        quit_button.centerx - quit_text.get_width() // 2,
        quit_button.centery - quit_text.get_height() // 2
    ))
        screen.blit(main_menu_text, (
        main_menu_button.centerx - main_menu_text.get_width() // 2,
        main_menu_button.centery - main_menu_text.get_height() // 2
    ))
        pygame.display.update()


