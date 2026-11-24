import asyncio
import pygame
import math

from variables import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ICE_COLOR,
    PLAYER_COLORS,
    BEAK_COLOR,
    BEAK_SIZE,
    PLAYER_RADIUS,
    SNOWBALL_RADIUS,
    SNOWBALL_COLOR
)


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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    await peer.submit_shoot_input()

    def draw(self, peer):
        self.screen.fill(ICE_COLOR)

        for peer_id, player in peer.game.state["players"].items():
            if player["state"] != "playing":
                continue

            color = PLAYER_COLORS[(int(peer_id) - 1) % len(PLAYER_COLORS)]

            pygame.draw.circle(
                self.screen,
                color,
                (int(player["x"]), int(player["y"])),
                PLAYER_RADIUS,
            )

            angle = math.radians(player["angle"])

            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)

            points = [
                (PLAYER_RADIUS, -BEAK_SIZE / 2),
                (PLAYER_RADIUS + BEAK_SIZE, 0),
                (PLAYER_RADIUS, BEAK_SIZE / 2),
            ]

            rotated_points = [
                (
                    player["x"] + x * cos_angle - y * sin_angle,
                    player["y"] + x * sin_angle + y * cos_angle,
                )
                for x, y in points
            ]

            pygame.draw.polygon(self.screen, BEAK_COLOR, rotated_points)

        for ball in peer.game.state["snowballs"]:
            pygame.draw.circle(
                self.screen,
                SNOWBALL_COLOR,
                (round(ball["x"]), round(ball["y"])),
                SNOWBALL_RADIUS,
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
