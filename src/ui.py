import pygame
#import pygame requirements.txt fileen?

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

player_x = 1920 // 2
player_y = 1080 // 2
player_radius = 25
player_color = (0, 100, 255)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    ice = (204, 255, 255)
    screen.fill(ice)

    pygame.draw.circle(
        screen,
        player_color,
        (player_x, player_y),
        player_radius
    )

    pygame.display.flip()
    clock.tick(60)
