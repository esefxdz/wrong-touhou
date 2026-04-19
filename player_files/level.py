import pygame
import time
from constants import WIDTH, HEIGHT, WHITE, RED, LIGHT_RED, GREEN, LIGHT_GREEN, DARK_GRAY, CYAN, YELLOW, TRANSPARENT_BLACK, LIGHT_GRAY, FONT_LARGE
from perks.perk_system import get_perk_choices, apply_perk

class LevelSystem:
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 10
        self.level_up_text_timer = 0
        self.pending_levels = 0  # unchosen perk level ups
        
        # pause-like system for level up screen
        self.paused = False
        self.last_click_time = 0
        self.click_cooldown = 0.6
        self.font = pygame.font.SysFont(None, FONT_LARGE)
        self.small_font = pygame.font.Font(None, 24)
        self.card_font = pygame.font.SysFont(None, 34)
        self.card_desc_font = pygame.font.SysFont(None, 26)
        
        # level line image backdrop
        try:
            self.line_image = pygame.image.load("textures/level_line.png").convert_alpha()
        except:
            self.line_image = pygame.Surface((600, 200), pygame.SRCALPHA)
            self.line_image.fill((80, 80, 160))
        
        # thinner strip - about 30% of screen height
        line_height = int(HEIGHT * 0.30)
        self.line_image = pygame.transform.scale(self.line_image, (WIDTH, line_height))
        
        # current perk choices shown on screen
        self._current_choices = []
        
        # reference to player, set when level up screen opens
        self._player_ref = None
        
        # icon image cache so we dont reload from disk every frame
        self._icon_cache = {}

    #------------------------------------------
    # xp and leveling / tracking progress
    #------------------------------------------
    def add_xp(self, amount):
        self.current_xp += amount
        if self.current_xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.current_xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        self.level_up_text_timer = 60
        self.pending_levels += 1
        self.paused = True

    def open_with_player(self, player):
        """Call this before drawing to wire in the player ref and generate fresh choices."""
        self._player_ref = player
        if not self._current_choices:
            self._current_choices = get_perk_choices(3)
        
    def check_reopen(self, event):
        """Press L to reopen level up screen if there are pending perks."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            if self.pending_levels > 0 and not self.paused:
                self.paused = True

    #------------------------------------------
    # xp bar / showing progress at top of screen
    #------------------------------------------
    def draw_xp_bar(self, screen):
        bar_width = 300
        bar_height = 10
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 45  # right underneath health bar
        
        fill_width = (self.current_xp / self.xp_to_next_level) * bar_width
        if fill_width > bar_width:
            fill_width = bar_width

        pygame.draw.rect(screen, DARK_GRAY, (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, CYAN, (x_pos, y_pos, fill_width, bar_height))
        
        lvl_text = self.small_font.render(f"Lvl {self.level}", True, (255, 255, 255))
        screen.blit(lvl_text, (x_pos - 50, y_pos - 4))
        
        if self.level_up_text_timer > 0:
            up_text = self.small_font.render("Level Up!", True, YELLOW)
            screen.blit(up_text, (x_pos + bar_width + 10, y_pos - 4))
            self.level_up_text_timer -= 1
        
        # show pending perks count
        if self.pending_levels > 0:
            pending_text = self.small_font.render(f"({self.pending_levels} pending - press L)", True, YELLOW)
            screen.blit(pending_text, (x_pos + bar_width + 10, y_pos - 4))

    #------------------------------------------
    # level up screen / showing perk cards
    #------------------------------------------
    def draw_level_up_screen(self, screen):
        """Draw the level up overlay with perk choices - called from main loop."""
        if not self.paused:
            return

        # transparent dark overlay
        dark_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_surface.fill(TRANSPARENT_BLACK)
        screen.blit(dark_surface, (0, 0))
        
        # backdrop strip
        line_rect = self.line_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(self.line_image, line_rect)
        
        # title
        title_str = f"Level Up!  ({self.pending_levels} available)"
        title = self.font.render(title_str, True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, line_rect.top + 15))

        # perk cards
        self._draw_perk_cards(screen, line_rect)

        # skip button
        skip_button = pygame.Rect(WIDTH // 2 - 100, line_rect.bottom - 60, 200, 45)
        skip_text = self.font.render("Skip", True, WHITE)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        pygame.draw.rect(screen, RED, skip_button)
        if skip_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LIGHT_RED, skip_button)
            current_time = time.time()
            if mouse_click[0] and current_time - self.last_click_time > self.click_cooldown:
                self.last_click_time = current_time
                self.paused = False  # pending_levels stays, player can reopen with L
        
        screen.blit(skip_text, (
            skip_button.centerx - skip_text.get_width() // 2,
            skip_button.centery - skip_text.get_height() // 2
        ))

    def _load_icon(self, path, size=56):
        """Load and cache a perk icon. Returns None if file is missing."""
        if path in self._icon_cache:
            return self._icon_cache[path]
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (size, size))
            self._icon_cache[path] = img
        except Exception:
            self._icon_cache[path] = None  # cache the miss so we dont retry every frame
        return self._icon_cache[path]

    def _draw_perk_cards(self, screen, line_rect):
        """Draw the 3 perk choice cards and handle clicks."""
        if not self._current_choices:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        # card sizing / spacing - taller to fit icon above text
        card_count = len(self._current_choices)
        card_w = 200
        card_h = 155
        icon_size = 56
        padding = 20
        total_w = card_count * card_w + (card_count - 1) * padding
        start_x = WIDTH // 2 - total_w // 2
        card_y = line_rect.top + 65

        for i, perk in enumerate(self._current_choices):
            card_x = start_x + i * (card_w + padding)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

            # hover highlight
            hovered = card_rect.collidepoint(mouse_pos)
            color = (80, 160, 80) if hovered else (50, 100, 50)
            pygame.draw.rect(screen, color, card_rect, border_radius=8)
            pygame.draw.rect(screen, GREEN, card_rect, 2, border_radius=8)

            # icon at the top of the card
            icon_path = perk.get("icon")
            icon_y = card_rect.top + 10
            if icon_path:
                icon = self._load_icon(icon_path, icon_size)
                if icon:
                    screen.blit(icon, (card_rect.centerx - icon_size // 2, icon_y))
                else:
                    # missing file fallback - draw a small placeholder square
                    pygame.draw.rect(screen, LIGHT_GRAY,
                                     (card_rect.centerx - icon_size // 2, icon_y, icon_size, icon_size),
                                     border_radius=4)

            # perk name below icon
            name_surf = self.card_font.render(perk["name"], True, WHITE)
            screen.blit(name_surf, (
                card_rect.centerx - name_surf.get_width() // 2,
                card_rect.top + icon_size + 18
            ))

            # perk description below name
            desc_surf = self.card_desc_font.render(perk["description"], True, (200, 255, 200))
            screen.blit(desc_surf, (
                card_rect.centerx - desc_surf.get_width() // 2,
                card_rect.top + icon_size + 52
            ))

            # click to apply
            if hovered and mouse_click[0]:
                current_time = time.time()
                if current_time - self.last_click_time > self.click_cooldown:
                    self.last_click_time = current_time
                    if self._player_ref:
                        apply_perk(self._player_ref, perk)
                    self.pending_levels -= 1
                    self._current_choices = []  # clear so next open gets fresh choices
                    if self.pending_levels <= 0:
                        self.paused = False
                    else:
                        # more pending levels? immediately show next set
                        self._current_choices = get_perk_choices(3)
