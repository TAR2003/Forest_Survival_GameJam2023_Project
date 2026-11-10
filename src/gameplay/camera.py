"""Camera placeholder until the follow camera lands."""


class Camera:
    def __init__(self, width=1280, height=720, *args, **kwargs):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
