import pygame
from constants import YELLOW

class WaveUI:
    def __init__(self, font_size=36):
        self.font = pygame.font.Font(None, font_size)
    
    def draw(self, surface, wave_director):
        total = getattr(wave_director, 'total_enemies_this_wave', len(wave_director.spawn_queue))
        spawned = total - len(wave_director.spawn_queue)
        
        text = f"DEBUG Wave {wave_director.current_wave} | Enemies Spawned: {spawned}/{total} | Queue Left: {len(wave_director.spawn_queue)}"
        surf = self.font.render(text, True, YELLOW)
        surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, surface.get_height() - 40))
