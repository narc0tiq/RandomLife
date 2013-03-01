from modules.randomlife.utils import Rect

class Room(Rect):
    def __init__(self, map, x, y, w, h):
        Rect.__init__(self, x, y, w, h)
        self.map = map

    def fill_room(self):
        for x in range(self.x1 + 1, self.x2 - 1):
            for y in range(self.y1 + 1, self.y2 - 1):
                self.map[x][y].pass_through = True
                self.map[x][y].see_through = True


def carve_h_tunnel(map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].pass_through = True
        map[x][y].see_through = True

def carve_v_tunnel(map, x, y1, y2):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].pass_through = True
        map[x][y].see_through = True

