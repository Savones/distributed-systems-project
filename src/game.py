from variables import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_RADIUS


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
            "hearts": 3,
            "score": 0,
            "state": "playing",
        }

    def process_input(self, peer_id, player_input):
        player = self.state["players"][str(peer_id)]

        if player["state"] != "playing":
            return

        x = max(
            PLAYER_RADIUS,
            min(player_input["x"], SCREEN_WIDTH - PLAYER_RADIUS),
        )

        y = max(
            PLAYER_RADIUS,
            min(player_input["y"], SCREEN_HEIGHT - PLAYER_RADIUS),
        )

        for other_id, other in self.state["players"].items():
            if other_id == str(peer_id) or other["state"] != "playing":
                continue

            distance_squared = (
                (x - other["x"]) ** 2
                + (y - other["y"]) ** 2
            )

            if distance_squared < (PLAYER_RADIUS * 2) ** 2:
                return

        player["x"] = x
        player["y"] = y
