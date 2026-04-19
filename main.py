import pygame
import random
from baddies import spawn_enemy
from constants import WIDTH, HEIGHT, BLACK, FPS
from collision_optimizer.hit_register import check_player_bullets_vs_enemies, check_enemy_bullets_vs_player, SpatialHash
from collision_optimizer.gpu_renderer import MasterRenderer
from collision_optimizer.projectile_manager import ProjectileManager
import numpy as np
from player_files.player import spaceship
from ui.pause import ppause
from ui.menu import mmenu
from ui.over import gover, reset_game
import maps.map_01 as map_01
import maps.map_02 as map_02
from ui.shop_menu.shop import ShopMenu
from director.wave_shenanigans import WaveTransitionTimer, draw_enemy_pointers

from director.wave_director import WaveDirector
from director.wave_ui import WaveUI
wave_ui = WaveUI()

pygame.init()

# game window - Initialize with OpenGL flags
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("will it work tho")

# Virtual surface for standard Pygame drawing
display_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
renderer = MasterRenderer(WIDTH, HEIGHT)

# picks a random map
available_maps = [map_01, map_02]

# initialize the game for the first time
current_map, background_image, player, enemies, projectile_manager, wave_director = reset_game(available_maps)
spatial_grid = SpatialHash(cell_size=100)

# fps counter
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.Font(None, 36)

#pause menu, didnt know where to put it
mmmenu = mmenu()
pause = ppause()
gover_menu = gover()
shop_menu = ShopMenu()
wave_timer = WaveTransitionTimer(delay_ms=3000)

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
        player.level_system.open_with_player(player)
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
            current_map, background_image, player, enemies, projectile_manager, wave_director = reset_game(available_maps)
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

    # shop menu area
    if shop_menu.active:
        shop_menu.draw(display_surface)
        renderer.render(display_surface, np.array([], dtype=np.float32), (0,0))
        pygame.display.flip()
        
        if not shop_menu.active:
            wave_director.generate_wave()
            shop_menu.fade_alpha = 0
            
        clock.tick(FPS)
        continue

    # camera
    cam_offset = player.get_camera_offset()

    # Clear virtual surface
    display_surface.fill((0, 0, 0, 0))

    # fill teh screen - draw background with camera offset
    display_surface.blit(background_image, (0, 0), (cam_offset[0], cam_offset[1], WIDTH, HEIGHT))
    current_time = pygame.time.get_ticks()

    # wave director area
    dt = 1.0 / FPS # logic runs locked to tick cycle length
    wave_director.update(dt)
    
    # purge defeated enemies so the director knows the map is clean
    spatial_grid.clear()
    alive_enemies = []
    for enemy in enemies:
        # keep alive enemies in the spatial hash for collision
        if not enemy.defeated:
            spatial_grid.insert(enemy.lolrect, enemy)
            alive_enemies.append(enemy)
        # keep defeated enemies until their dropped orbs are all collected
        elif enemy.dropped_orbs:
            alive_enemies.append(enemy)
    enemies[:] = alive_enemies
    
    # wave transition delay
    wave_timer.check_transition(wave_director.is_wave_complete(), pygame.time.get_ticks(), shop_menu)

    wave_ui.draw(display_surface, wave_director)

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
    
    # Optimized collision detection logic
    check_player_bullets_vs_enemies(projectile_manager, enemies, spatial_grid, player)
    check_enemy_bullets_vs_player(projectile_manager, player)

    # enemy area / probably needs changing
    for enemy in enemies:
        enemy.active_enemies_list = enemies
        enemy.update(display_surface, player, projectile_manager)
        enemy.draw(display_surface, cam_offset)

    # Ensure wave ends if only orbs remain
    living_enemies_count = sum(1 for e in enemies if not e.defeated)
    wave_is_over = (living_enemies_count == 0 and len(wave_director.spawn_queue) == 0)

    # orb pass — runs for all enemies including defeated ones so dropped orbs persist
    for enemy in enemies:
        enemy.update_orbs(player, force_magnet=wave_is_over)
        enemy.draw_orbs(display_surface, cam_offset)

    # draw straggler pointers if under 10 enemies left
    draw_enemy_pointers(display_surface, enemies, wave_director, cam_offset, WIDTH, HEIGHT)

    # Calculate vectorized physics updates for all active bullets
    projectile_manager.update(current_map.MAP_WIDTH, current_map.MAP_HEIGHT)

    # FINAL GPU RENDER
    vbo_data = projectile_manager.get_vbo_data()
    renderer.render(display_surface, vbo_data, cam_offset)

    pygame.display.flip()
    clock.tick(FPS)

# just quittin
pygame.quit()