import pygame
import os
import sys
import time
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants
from constants import WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN, LIGHT_GREEN, RED, LIGHT_RED, CYAN, DARK_GRAY, LIGHT_GRAY, FONT_LARGE, FONT_MEDIUM, FONT_SMALL
from player_files import PLAYER_REGISTRY

class CharacterSelect:

    #------------------------------------------
    # initialization / fonts and state
    # target: @everyone
    #------------------------------------------
    def __init__(self):
        self.selected_name = None
        self.font_large  = pygame.font.SysFont(None, FONT_LARGE)
        self.font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
        self.font_small  = pygame.font.SysFont(None, FONT_SMALL)
        self._portrait_cache = {}
        self.last_click_time = 0
        self.click_cooldown  = 0.4
        
        self.background = pygame.image.load("textures/character_selection.jpg")
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

    #------------------------------------------
    # portrait loader / cached per character
    # target: @everyone
    #------------------------------------------
    def _load_portrait(self, cls, size=120):
        name = cls.NAME
        if name not in self._portrait_cache:
            port = None
            if cls.PORTRAIT_PATH:
                full_path = os.path.join("player_files", cls.PORTRAIT_PATH)
                try:
                    img = pygame.image.load(full_path).convert_alpha()
                    fw, fh = cls.SPRITE_SIZE
                    frame = img.subsurface(pygame.Rect(0, 0, fw, fh))
                    port = pygame.transform.scale(frame, (size, size))
                except Exception:
                    pass
            if port is None:
                port = pygame.Surface((size, size))
                port.fill(DARK_GRAY)
            self._portrait_cache[name] = port
        return self._portrait_cache[name]

    #------------------------------------------
    # run / blocks until player confirms a character
    # target: @everyone
    #------------------------------------------
    def run(self, surface, clock, renderer):
        self.selected_name = None
        chars = list(PLAYER_REGISTRY.items())

        # wait for mouse to be fully released before accepting any input
        # this prevents click carry-over from the previous screen
        while pygame.mouse.get_pressed()[0]:
            pygame.event.pump()
            clock.tick(FPS)

        while self.selected_name is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # use event-driven clicks instead of get_pressed to avoid carry-over
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    now = time.time()
                    if now - self.last_click_time > self.click_cooldown:
                        mouse_pos = event.pos
                        card_w = 200
                        card_h = 280
                        gap    = 40
                        total_w = len(chars) * card_w + (len(chars) - 1) * gap
                        start_x = WIDTH // 2 - total_w // 2
                        card_y  = HEIGHT // 2 - card_h // 2
                        for i, (name, cls) in enumerate(chars):
                            cx = start_x + i * (card_w + gap)
                            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
                            if card_rect.collidepoint(mouse_pos):
                                self.last_click_time = now
                                self.selected_name = name

            # draw background
            surface.blit(self.background, (0, 0))

            # title
            title = self.font_large.render("Choose your character", True, WHITE)
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

            mouse_pos = pygame.mouse.get_pos()

            card_w = 200
            card_h = 280
            gap    = 40
            total_w = len(chars) * card_w + (len(chars) - 1) * gap
            start_x = WIDTH // 2 - total_w // 2
            card_y  = HEIGHT // 2 - card_h // 2

            for i, (name, cls) in enumerate(chars):
                cx = start_x + i * (card_w + gap)
                card_rect = pygame.Rect(cx, card_y, card_w, card_h)
                hovered = card_rect.collidepoint(mouse_pos)

                bg_color = LIGHT_GREEN if hovered else DARK_GRAY
                pygame.draw.rect(surface, bg_color, card_rect, border_radius=10)
                pygame.draw.rect(surface, GREEN if hovered else LIGHT_GRAY, card_rect, 2, border_radius=10)

                # portrait
                portrait = self._load_portrait(cls, size=120)
                surface.blit(portrait, (cx + card_w // 2 - 60, card_y + 15))

                # name
                name_surf = self.font_medium.render(cls.NAME, True, WHITE)
                surface.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, card_y + 150))

                # description word-wrapped
                words = cls.DESCRIPTION.split()
                lines, line = [], ""
                for w in words:
                    test = (line + " " + w).strip()
                    if self.font_small.size(test)[0] < card_w - 16:
                        line = test
                    else:
                        lines.append(line)
                        line = w
                lines.append(line)
                for li, l in enumerate(lines[:3]):
                    ls = self.font_small.render(l, True, LIGHT_GRAY)
                    surface.blit(ls, (cx + card_w // 2 - ls.get_width() // 2, card_y + 185 + li * 22))

            renderer.render(surface, np.array([], dtype=np.float32), (0, 0))
            pygame.display.flip()
            clock.tick(FPS)

        return self.selected_name
