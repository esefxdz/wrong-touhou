import pygame

class WaveTransitionTimer:
    def __init__(self, delay_ms=3000):
        # basic timer settings
        self.delay_ms = delay_ms
        self.waiting = False
        self.wait_start_time = 0
        
    def check_transition(self, is_complete, current_time, shop_menu):
        # wait if wave is finished but we haven't opened shop yet
        if is_complete:
            if not self.waiting and not shop_menu.active:
                self.waiting = True
                self.wait_start_time = current_time
                
            # check the delay
            if self.waiting and not shop_menu.active:
                elapsed = current_time - self.wait_start_time
                if elapsed >= self.delay_ms:
                    # boom shop time
                    shop_menu.trigger()
                    self.waiting = False
        else:
            # resets when new wave kicks in
            self.waiting = False

def draw_enemy_pointers(screen, enemies, wave_director, cam_offset, width, height):
    """Draws arrows pointing to off-screen enemies if there are 10 or fewer total enemies remaining in the wave."""
    if len(wave_director.spawn_queue) > 0:
        return
        
    living_enemies = [e for e in enemies if not e.defeated]
    if len(living_enemies) == 0 or len(living_enemies) > 10:
        return
        
    # Screen center
    cx, cy = width / 2, height / 2
    margin = 30  # Keep arrow slightly away from the absolute screen edge
    
    import math
    for enemy in living_enemies:
        ex = enemy.lolrect.centerx - cam_offset[0]
        ey = enemy.lolrect.centery - cam_offset[1]
        
        is_offscreen = (ex < 0 or ex > width or ey < 0 or ey > height)
        if not is_offscreen:
            continue
            
        dx = ex - cx
        dy = ey - cy
        
        if dx == 0 and dy == 0:
            continue
            
        # Ray-box intersection to find edge point
        scale_x = float('inf')
        scale_y = float('inf')
        
        if dx > 0:
            scale_x = (width - margin - cx) / dx
        elif dx < 0:
            scale_x = (margin - cx) / dx
            
        if dy > 0:
            scale_y = (height - margin - cy) / dy
        elif dy < 0:
            scale_y = (margin - cy) / dy
            
        scale = min(scale_x, scale_y)
        
        ax = cx + dx * scale
        ay = cy + dy * scale
        
        # Calculate arrow triangle points
        angle = math.atan2(dy, dx)
        arrow_size = 18
        
        p1 = (ax, ay)
        p2 = (ax - arrow_size * math.cos(angle - 0.5), ay - arrow_size * math.sin(angle - 0.5))
        p3 = (ax - arrow_size * math.cos(angle + 0.5), ay - arrow_size * math.sin(angle + 0.5))
        
        # solid red arrow with bright white outline
        pygame.draw.polygon(screen, (255, 30, 30), [p1, p2, p3])
        pygame.draw.polygon(screen, (255, 255, 255), [p1, p2, p3], 2)

