import asyncio
import pygame


class GameUI():

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.ice = (204, 255, 255)
        self.clock = pygame.time.Clock()

        self.player_x = 1920 // 2
        self.player_y = 1080 // 2
        self.player_radius = 25
        self.player_color = (0, 100, 255)

        self.running = True

    async def events(self, peer):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                await self.motion(peer, x, y)

    def draw(self):
        self.screen.fill(self.ice)

        pygame.draw.circle(
            self.screen,
            self.player_color,
            (self.player_x, self.player_y),
            self.player_radius
        )

        pygame.display.flip()

    async def motion(self, peer, x, y):

        await peer.submit_player_input(peer.peer_id, x, y)

    async def run(self, peer):
        while self.running:
            await self.events(peer)
            self.draw()
            self.clock.tick(60)
            await asyncio.sleep(0)

        pygame.quit()
