import pygame
from baddies.enemy import rumia
from constants import WIDTH, HEIGHT, BLACK
from hit_register import boss_hit, player_hit
from player import spaceship
from baddies.enemy import rumia

pygame.init()

# game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("will it work tho")

# background image
background_image = pygame.image.load("background.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

#player variable and other variables from files
x = 100
y = 100
player = spaceship(x, y)
boss = rumia()

# fps counter
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill teh screen
    screen.blit(background_image, (0, 0))
    current_time = pygame.time.get_ticks()

    # fps counter ingame
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    # player area
    keys = pygame.key.get_pressed()
    player.draw(screen)
    player.move(keys)
    player.shoot()
    player.shoot_update(screen)
    player_hit(player.bullets, boss.lolrect)

    #enemy area
    boss.draw(screen)
    boss.fire()
    boss.update_fire(screen)
    boss.move(WIDTH)
    boss_hit(boss.fires, player.spaceship_rect)


    pygame.display.flip()
    clock.tick(60)

# just quittin
pygame.quit()
