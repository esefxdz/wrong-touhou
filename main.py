import pygame
from baddies.enemy import rumia
from constants import WIDTH, HEIGHT, BLACK
from hit_register import boss_hit, player_hit
from player_files.player import spaceship
from baddies.enemy import rumia
from ui.pause import ppause
from ui.menu import mmenu
from ui.over import gover

pygame.init()

# game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("will it work tho")

# background image
background_image = pygame.image.load("textures/background.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

#player variable and other variables from files
x = 100
y = 100
player = spaceship(x, y)
enemies = []
enemy_spawn_timer = 0
enemy_spawn_interval = 2000  # spawn every 2 seconds
enemies_per_wave = 3

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
            player = spaceship(100, 100)
            enemies = []
            gover_menu.replay = False
            
        pygame.display.flip()
        continue

    # death check
    if player.hit_count >= player.max_hp:
        gover_menu.set_stats(player.enemies_killed, player.damage_dealt)
        gover_menu.game_over = True
        continue

    # fill teh screen
    screen.blit(background_image, (0, 0))
    current_time = pygame.time.get_ticks()

    #enemy spawns
    if current_time - enemy_spawn_timer > enemy_spawn_interval:
        for _ in range(enemies_per_wave):
            enemies.append(rumia(player))
        enemy_spawn_timer = current_time


    # fps counter ingame
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    # player area
    keys = pygame.key.get_pressed()
    player.draw(screen)
    player.draw_health(screen)
    player.level_system.draw_xp_bar(screen)
    player.move(keys)
    player.shoot()
    player.shoot_update(screen)
    for enemy in enemies:
        if not enemy.defeated:
            player_hit(player, enemy.lolrect, enemy.take_hit)

    #enemy area
    alive_enemies = []
    for enemy in enemies:
        enemy.draw(screen)
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