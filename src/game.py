import math

from variables import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_RADIUS, PLAYER_SPEED, BEAK_ROTATION_SPEED


class Game:
    def __init__(self):
        self.state = {
            "sequence_number": 0,
            "players": {},
            "snowballs": [],
        }

    def add_player(self, peer_id):
        self.state["players"][str(peer_id)] = {
            "x": 100,
            "y": 100,
            "target_x": 100,
            "target_y": 100,
            "angle": 0.0,
            "hearts": 3,
            "score": 0,
            "state": "playing",
        }

    def process_input(self, peer_id, player_input):
        player = self.state["players"][str(peer_id)]

        if player["state"] != "playing":
            return

        player["target_x"] = max(
            PLAYER_RADIUS,
            min(player_input["x"], SCREEN_WIDTH - PLAYER_RADIUS),
        )
        player["target_y"] = max(
            PLAYER_RADIUS,
            min(player_input["y"], SCREEN_HEIGHT - PLAYER_RADIUS),
        )

    def can_move_to(self, peer_id, x, y):
        for other_id, other in self.state["players"].items():
            if other_id == str(peer_id) or other["state"] != "playing":
                continue

            distance_squared = (
                (x - other["x"]) ** 2
                + (y - other["y"]) ** 2
            )

            if distance_squared < (PLAYER_RADIUS * 2) ** 2:
                return False

        return True

    def update(self, dt):
        for peer_id, player in self.state["players"].items():
            if player["state"] != "playing":
                continue

            player["angle"] = (
                player["angle"] + BEAK_ROTATION_SPEED * dt
            ) % 360

            dx = player["target_x"] - player["x"]
            dy = player["target_y"] - player["y"]
            distance = math.hypot(dx, dy)

            if distance == 0:
                continue

            movement = min(PLAYER_SPEED * dt, distance)

            steps = max(1, math.ceil(movement / (PLAYER_RADIUS / 2)))
            step_x = (dx / distance) * movement / steps
            step_y = (dy / distance) * movement / steps

            for _ in range(steps):
                x = player["x"] + step_x
                y = player["y"] + step_y

                if not self.can_move_to(peer_id, x, y):
                    break

                player["x"] = x
                player["y"] = y
