import pygame

class SpatialHash:
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.grid = {}

    def _get_cell_coords(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        self.grid = {}

    def insert(self, rect, item):
        start_x, start_y = self._get_cell_coords(rect.left, rect.top)
        end_x, end_y = self._get_cell_coords(rect.right, rect.bottom)
        for cx in range(start_x, end_x + 1):
            for cy in range(start_y, end_y + 1):
                key = (cx, cy)
                if key not in self.grid:
                    self.grid[key] = []
                self.grid[key].append(item)

    def query(self, rect):
        start_x, start_y = self._get_cell_coords(rect.left, rect.top)
        end_x, end_y = self._get_cell_coords(rect.right, rect.bottom)
        candidates = set()
        for cx in range(start_x, end_x + 1):
            for cy in range(start_y, end_y + 1):
                key = (cx, cy)
                if key in self.grid:
                    for item in self.grid[key]:
                        candidates.add(item)
        return candidates

import numpy as np

def check_player_bullets_vs_enemies(proj_manager, enemies, spatial_hash, player):
    """Checks player bullets against enemies stored in the spatial hash."""
    pl_mask = proj_manager.active & (proj_manager.owner == 0)
    if not np.any(pl_mask): return
    
    pl_idx = np.where(pl_mask)[0]
    
    for idx in pl_idx:
        bx = proj_manager.pos_x[idx]
        by = proj_manager.pos_y[idx]
        # use bullet radius from array, though in original it was hardcoded 20x40. We can just use the provided radius.
        br = proj_manager.radius[idx]
        w, h = max(20, br*2), max(40, br*2)
        
        bullet_rect = pygame.Rect(0, 0, w, h)
        bullet_rect.center = (int(bx), int(by))
        
        nearby_enemies = spatial_hash.query(bullet_rect)
        for enemy in nearby_enemies:
            if not enemy.defeated and bullet_rect.colliderect(enemy.lolrect):
                enemy.take_hit()
                player.damage_dealt += 1
                player.level_system.add_xp(1)
                # consume bullet in the array
                proj_manager.active[idx] = False
                proj_manager.active_count -= 1
                break

def check_enemy_bullets_vs_player(proj_manager, player):
    """Vectorized check for all enemy bullets against the single player."""
    en_mask = proj_manager.active & (proj_manager.owner == 1)
    if not np.any(en_mask): return
    
    px, py = player.spaceship_rect.center
    
    dx = proj_manager.pos_x[en_mask] - px
    dy = proj_manager.pos_y[en_mask] - py
    dist_sq = dx**2 + dy**2
    
    # 25 is roughly half of player's 50x50 rect
    radii = proj_manager.radius[en_mask] + 25.0
    hit_mask = dist_sq < (radii ** 2)
    
    if np.any(hit_mask):
        hits_count = np.sum(hit_mask)
        for _ in range(hits_count):
            player.take_hit()
            
        # disable the bullets that hit
        active_indices = np.where(en_mask)[0]
        hit_indices = active_indices[hit_mask]
        proj_manager.active[hit_indices] = False
        proj_manager.active_count -= len(hit_indices)
