import pygame
import random
from baddies import spawn_enemy
from constants import WIDTH, HEIGHT, BLACK
from collision_optimizer.hit_register import check_player_bullets_vs_enemies, check_enemy_bullets_vs_player, SpatialHash
from collision_optimizer.gpu_renderer import MasterRenderer
from collision_optimizer.projectile_manager import ProjectileManager
import numpy as np
from player_files.player import spaceship
from ui.pause import ppause
from ui.menu import mmenu
from ui.over import gover
import maps.map_01 as map_01
import maps.map_02 as map_02

pygame.init()

# game window - Initialize with OpenGL flags
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("will it work tho")

# Virtual surface for standard Pygame drawing
display_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
renderer = MasterRenderer(WIDTH, HEIGHT)

# pick a random map
available_maps = [map_01, map_02]

def reset_game():
    # Get fresh map and assets
    m = random.choice(available_maps)
    bg = pygame.image.load(m.MAP_IMAGE)
    bg = pygame.transform.scale(bg, (m.MAP_WIDTH, m.MAP_HEIGHT))
    
    # Reset objects
    p = spaceship(100, 100, m.MAP_WIDTH, m.MAP_HEIGHT)
    pm = ProjectileManager()
    
    # Reset all map wave timers
    for wave in m.ENEMY_WAVES:
        wave.pop("timer", None)
        
    return m, bg, p, [], pm

current_map, background_image, player, enemies, projectile_manager = reset_game()
spatial_grid = SpatialHash(cell_size=100)

# fps counter
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.Font(None, 36)

#pause menu, didnt know where to put it
mmmenu = mmenu()
pause = ppause()
gover_menu = gover()

mmmenu.run(display_surface, clock, renderer)

in_menu = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not in_menu and not pause.paused:
            pause.pause_toggle(event)
            player.level_system.check_reopen(event)

    if in_menu:
        mmmenu.run(display_surface, clock, renderer)
        in_menu = False
        continue
    else:
        pass

    if pause.paused:
        pause.blit(display_surface)
        pause.pause_button(display_surface)
        if pause.menu:
            pause.menu = False
            in_menu = True
            
        renderer.render(display_surface, np.array([], dtype=np.float32), (0,0))
        pygame.display.flip()
        continue

    #level up menu display
    if player.level_system.paused:
        player.level_system.draw_level_up_screen(display_surface)
        renderer.render(display_surface, np.array([], dtype=np.float32), (0,0))
        pygame.display.flip()
        continue

    #game over menu area
    if gover_menu.game_over:
        gover_menu.blit(display_surface)
        gover_menu.buttons(display_surface)
        
        if gover_menu.replay:
            # Clean Reset
            current_map, background_image, player, enemies, projectile_manager = reset_game()
            gover_menu.replay = False
            gover_menu.game_over = False
            continue
            
        renderer.render(display_surface, np.array([], dtype=np.float32), (0,0))
        pygame.display.flip()
        continue

    # death check
    if player.hit_count >= player.max_hp:
        gover_menu.set_stats(player.enemies_killed, player.damage_dealt)
        gover_menu.game_over = True
        continue

    # camera
    cam_offset = player.get_camera_offset()

    # Clear virtual surface
    display_surface.fill((0, 0, 0, 0))

    # fill teh screen - draw background with camera offset
    display_surface.blit(background_image, (0, 0), (cam_offset[0], cam_offset[1], WIDTH, HEIGHT))
    current_time = pygame.time.get_ticks()

    # enemy spawns logic / gonna be removed with new wave director system
    for wave in current_map.ENEMY_WAVES:
        if "timer" not in wave:
            wave["timer"] = 0
        if current_time - wave["timer"] > wave["interval"]:
            for _ in range(wave["count"]):
                enemies.append(spawn_enemy(wave["enemy"], player))
            wave["timer"] = current_time

    # fps counter ingame
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    display_surface.blit(fps_text, (10, 10))

    # player area
    keys = pygame.key.get_pressed()
    player.draw(display_surface, cam_offset)
    player.draw_health(display_surface)
    player.level_system.draw_xp_bar(display_surface)
    player.move(keys)
    player.shoot(cam_offset, projectile_manager)
    
    # Optimized collision detection logic ... (unchanged)
    spatial_grid.clear()
    for enemy in enemies:
        if not enemy.defeated:
            spatial_grid.insert(enemy.lolrect, enemy)
    check_player_bullets_vs_enemies(projectile_manager, enemies, spatial_grid, player)
    check_enemy_bullets_vs_player(projectile_manager, player)

    # enemy area / probably needs changing
    for enemy in enemies:
        enemy.update(display_surface, player, projectile_manager)
        enemy.draw(display_surface, cam_offset)

    # Calculate vectorized physics updates for all active bullets
    projectile_manager.update(current_map.MAP_WIDTH, current_map.MAP_HEIGHT)

    # FINAL GPU RENDER
    vbo_data = projectile_manager.get_vbo_data()
    renderer.render(display_surface, vbo_data, cam_offset)

    pygame.display.flip()
    clock.tick(60)

# just quittin
pygame.quit()