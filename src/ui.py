import asyncio
import pygame

from variables import SCREEN_WIDTH, SCREEN_HEIGHT, ICE_COLOR, PLAYER_COLORS, PLAYER_RADIUS


class GameUI():

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2

        self.running = True

    async def events(self, peer):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                await self.motion(peer, x, y)

    def draw(self, peer):
        self.screen.fill(ICE_COLOR)

        for peer_id, player in peer.game_state["players"].items():
            if player["state"] != "playing":
                continue

            color = PLAYER_COLORS[(int(peer_id) - 1) % len(PLAYER_COLORS)]

            pygame.draw.circle(
                self.screen,
                color,
                (int(player["x"]), int(player["y"])),
                PLAYER_RADIUS,
            )

        pygame.display.flip()

    async def motion(self, peer, x, y):

        await peer.submit_player_input(peer.peer_id, x, y)

    async def run(self, peer):
        while self.running:
            await self.events(peer)

            if not self.running:
                break

            self.draw(peer)
            await asyncio.sleep(1 / 60)

        pygame.quit()
