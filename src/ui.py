import asyncio
import pygame


class GameUI():

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.ice = (204, 255, 255)
        self.clock = pygame.time.Clock()

        self.player_x = 500 // 2
        self.player_y = 500 // 2
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

    def draw(self, peer):
        self.screen.fill(self.ice)

        for peer_id, player in peer.game_state["players"].items():
            if player["state"] != "playing":
                continue

            color = (
                self.player_color
                if peer_id == str(peer.peer_id)
                else (255, 100, 100)
            )

            pygame.draw.circle(
                self.screen,
                color,
                (int(player["x"]), int(player["y"])),
                self.player_radius,
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
