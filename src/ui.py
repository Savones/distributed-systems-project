import pygame

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    ice = (204, 255, 255)
    screen.fill(ice)

    pygame.display.flip()
    clock.tick(60)
