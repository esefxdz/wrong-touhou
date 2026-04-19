import pygame
import numpy as np

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
    # Only look at active enemy-owned bullets
    en_mask = proj_manager.active & (proj_manager.owner == 1)
    if not np.any(en_mask):
        return

    px, py = player.spaceship_rect.center

    # Reconstruct each bullet's movement segment for this frame.
    # update() already moved bullets forward by velocity, so previous pos = current - velocity.
    cur_x, cur_y = proj_manager.pos_x[en_mask], proj_manager.pos_y[en_mask]
    vx,    vy    = proj_manager.vel_x[en_mask],  proj_manager.vel_y[en_mask]
    prv_x, prv_y = cur_x - vx, cur_y - vy

    # Find the closest point on each segment to the player centre (swept, no tunneling).
    # t is the normalised distance along the segment clamped to [0, 1].
    seg_x, seg_y = cur_x - prv_x, cur_y - prv_y
    seg_len_sq   = seg_x**2 + seg_y**2
    t = ((px - prv_x)*seg_x + (py - prv_y)*seg_y) / np.where(seg_len_sq > 0, seg_len_sq, 1.0)
    t = np.clip(t, 0.0, 1.0)
    close_x = prv_x + t * seg_x
    close_y = prv_y + t * seg_y

    # Squared distance from that closest point to the player centre
    dist_sq  = (close_x - px)**2 + (close_y - py)**2
    bullet_r = proj_manager.radius[en_mask]

    # Two circle hitboxes — these are the only player hitboxes:
    #   hitbox_radius : tiny bright-orange dot  → real damage, bullet consumed
    #   graze_radius  : larger invisible ring    → earns XP, bullet kept
    is_hit   = dist_sq < (player.hitbox_radius + bullet_r)**2
    is_graze = ~is_hit & (dist_sq < (player.graze_radius + bullet_r)**2)

    indices = np.where(en_mask)[0]

    # Real hits: deal damage and consume the bullet
    if np.any(is_hit):
        hit_idx = indices[is_hit]
        for _ in hit_idx:
            player.take_hit()
        proj_manager.active[hit_idx] = False
        proj_manager.active_count -= len(hit_idx)

    # Grazes: reward XP once per bullet (deduped via grazed_this_frame set, cleared each draw call)
    if np.any(is_graze):
        for idx in indices[is_graze]:
            if int(idx) not in player.grazed_this_frame:
                player.grazed_this_frame.add(int(idx))
                player.level_system.add_xp(0.2)
