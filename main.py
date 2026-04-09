import pygame
import random
from baddies import spawn_enemy
from constants import WIDTH, HEIGHT, BLACK
from hit_register import boss_hit, player_hit
from player_files.player import spaceship
from ui.pause import ppause
from ui.menu import mmenu
from ui.over import gover
import maps.map_01 as map_01
import maps.map_02 as map_02

pygame.init()

# game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("will it work tho")

# pick a random map
available_maps = [map_01, map_02]
current_map = random.choice(available_maps)

# background image - sized to full map
background_image = pygame.image.load(current_map.MAP_IMAGE)
background_image = pygame.transform.scale(background_image, (current_map.MAP_WIDTH, current_map.MAP_HEIGHT))

#player variable and other variables from files
player = spaceship(100, 100, current_map.MAP_WIDTH, current_map.MAP_HEIGHT)
enemies = []

# fps counter
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.Font(None, 36)

#pause menu, didnt know where to put it
mmmenu = mmenu()
pause = ppause()
gover_menu = gover()

mmmenu.run(screen, clock)

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
        mmmenu.run(screen, clock)
        in_menu = False
        continue
    else:
        pass

    if pause.paused:
        pause.blit(screen)
        pause.pause_button(screen)
        if pause.menu:
            pause.menu = False
            in_menu = True
            
        pygame.display.flip()
        continue

    if player.level_system.paused:
        player.level_system.draw_level_up_screen(screen)
        pygame.display.flip()
        continue

    if gover_menu.game_over:
        gover_menu.blit(screen)
        gover_menu.buttons(screen)
        
        if gover_menu.replay:
            # Reset game state
            player = spaceship(100, 100, current_map.MAP_WIDTH, current_map.MAP_HEIGHT)
            enemies = []
            gover_menu.replay = False
            
        pygame.display.flip()
        continue

    # death check
    if player.hit_count >= player.max_hp:
        gover_menu.set_stats(player.enemies_killed, player.damage_dealt)
        gover_menu.game_over = True
        continue

    # camera
    cam_offset = player.get_camera_offset()

    # fill teh screen - draw background with camera offset
    screen.blit(background_image, (0, 0), (cam_offset[0], cam_offset[1], WIDTH, HEIGHT))
    current_time = pygame.time.get_ticks()

    #enemy spawns - each wave type from the map has its own timer
    for wave in current_map.ENEMY_WAVES:
        if "timer" not in wave:
            wave["timer"] = 0
        if current_time - wave["timer"] > wave["interval"]:
            for _ in range(wave["count"]):
                enemies.append(spawn_enemy(wave["enemy"], player))
            wave["timer"] = current_time


    # fps counter ingame (UI - no offset)
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    # player area
    keys = pygame.key.get_pressed()
    player.draw(screen, cam_offset)
    player.draw_health(screen)
    player.level_system.draw_xp_bar(screen)
    player.move(keys)
    player.shoot(cam_offset)
    player.shoot_update(screen, cam_offset)
    for enemy in enemies:
        if not enemy.defeated:
            player_hit(player, enemy.lolrect, enemy.take_hit)

    #enemy area
    alive_enemies = []
    for enemy in enemies:
        enemy.draw(screen, cam_offset)
        enemy.fire()
        enemy.update(screen)
        boss_hit(enemy.fires, player.spaceship_rect, player.take_hit)
        if not enemy.defeated or len(enemy.fires) > 0:
            alive_enemies.append(enemy)
    enemies = alive_enemies

    pygame.display.flip()
    clock.tick(60)

# just quittin
pygame.quit()