"""Side-view camera that follows the player and stays inside the zone."""


class Camera:
    def __init__(self, view_width: int, view_height: int, zone_width: int, zone_height: int = 0):
        self.view_width = view_width
        self.view_height = view_height
        self.zone_width = max(view_width, zone_width)
        self.zone_height = zone_height
        self.x = 0.0
        self.y = 0.0

    def follow(self, player_x: float, player_y: float):
        """Keep the player left of center and never show past the zone edges."""
        target_x = player_x - self.view_width * 0.35
        max_x = max(0, self.zone_width - self.view_width)
        self.x = min(max(0.0, target_x), float(max_x))
        if self.zone_height > self.view_height:
            target_y = player_y - self.view_height * 0.55
            max_y = self.zone_height - self.view_height
            self.y = min(max(0.0, target_y), float(max_y))
        else:
            self.y = 0.0

    def world_to_screen(self, x: float, y: float):
        return (int(x - self.x), int(y - self.y))
