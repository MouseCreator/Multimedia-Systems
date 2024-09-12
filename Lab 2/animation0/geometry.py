
class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def move_by(self, by_x, by_y):
        return Position(self.x+by_x, self.y+by_y)