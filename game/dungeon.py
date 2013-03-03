import tcod
from game import const
from game import utils

class Tile:
    def __init__(self, pass_through, see_through = None):
        self.pass_through = pass_through

        if(see_through is None):
            see_through = pass_through
        self.see_through = see_through
        self.explored = False

    def render(self, x, y, map):
        is_visible = map.fov_map.is_in_fov(x, y)
        is_wall = not self.pass_through

        color = const.COLOR_DARKNESS
        if is_visible:
            self.explored = True
            if is_wall:
                color = const.COLOR_LIGHT_WALL
            else:
                color = const.COLOR_LIGHT_GROUND
        else: # not in fov
            if not self.explored:
                color = const.COLOR_DARKNESS
            elif is_wall:
                color = const.COLOR_DARK_WALL
            else:
                color = const.COLOR_DARK_GROUND

        map.console.set_char_background(x, y, color)


class Room(utils.Rect):
    def __init__(self, map, x, y, w, h):
        utils.Rect.__init__(self, x, y, w, h)
        self.map = map

    def carve(self):
        for x in range(self.x1 + 1, self.x2 - 1):
            for y in range(self.y1 + 1, self.y2 - 1):
                self.map.tiles[x][y].pass_through = True
                self.map.tiles[x][y].see_through = True


class Entity:
    def __init__(self, x, y, char, color):
        self.map = None
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.on_move = []

    def can_pass(self, dx, dy):
        cell = self.map.tiles[self.x + dx][self.y + dy]
        return cell.pass_through

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        if self.can_pass(dx, dy):
            self.x += dx
            self.y += dy

        for f in self.on_move:
            f(self)

    def draw(self, console):
        """ Draw self to the passed-in console """
        if self.map.fov_map.is_in_fov(self.x, self.y):
            console.set_default_foreground(self.color)
            console.put_char(self.x, self.y, self.char)

    def clear(self, console):
        """ Remove self from the passed-in console """
        console.put_char(self.x, self.y, ' ')


class Map:
    def __init__(self, console):
        self.tiles = [[ Tile(False) for y in range(console.height)] for x in range(console.width)]
        self.rooms = []
        self.entities = []
        self.console = console
        self.fov_map = tcod.Map(console.width, console.height)

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.map = self

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.clear(self.console)

    def render(self):
        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                self.tiles[x][y].render(x, y, self)

        for e in self.entities:
            e.draw(self.console)

    def post_render(self):
        for e in self.entities:
            e.clear(self.console)

    def generate(self):
        for unused in range(const.ROOM_COUNT):
            w = tcod.random.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
            h = tcod.random.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
            # No off-screen rooms, okay?
            x = tcod.random.get_int(self.console.width - w - 1)
            y = tcod.random.get_int(self.console.height - h - 1)

            new_room = Room(self, x, y, w, h)
            is_overlapping = False
            for other_room in self.rooms:
                if new_room.intersects(other_room):
                    is_overlapping = True
                    break

            if is_overlapping: continue # forget this room, make a new one

            self.rooms.append(new_room)
        self.carve_rooms()

        for x in range(len(self.tiles)):
            for y in range(len(self.tiles[x])):
                tile = self.tiles[x][y]
                self.fov_map.set_properties(x, y, tile.see_through, tile.pass_through)

    def carve_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].pass_through = True
            self.tiles[x][y].see_through = True

    def carve_v_tunnel(self, x, y1, y2):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].pass_through = True
            self.tiles[x][y].see_through = True

    def carve_rooms(self):
        for i in range(len(self.rooms)):
            self.rooms[i].carve()

            if i == 0: continue # no tunnel to carve for first room

            start_point = self.rooms[i-1].center()
            end_point = self.rooms[i].center()

            if tcod.random.get_int(20) >= 12: # slight bias is intended
                self.carve_h_tunnel(start_point[0], end_point[0], start_point[1])
                self.carve_v_tunnel(end_point[0], start_point[1], end_point[1])
            else:
                self.carve_v_tunnel(start_point[0], start_point[1], end_point[1])
                self.carve_h_tunnel(start_point[0], end_point[0], end_point[1])

    def label_rooms(self):
        labels = utils.label_generator('A')
        for r in self.rooms:
            x, y = r.center()
            label = Entity(x, y, labels.next(), const.COLOR_LABEL)
            self.add_entity(label)

