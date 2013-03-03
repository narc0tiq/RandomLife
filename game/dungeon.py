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
        is_visible = map.is_visible(x, y)
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
    def __init__(self, map):
        utils.Rect.__init__(self, 0, 0, 0, 0)
        self.map = map

    def generate(self, x=None, y=None, w=None, h=None):
        if w is None:
            w = tcod.random.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
        if h is None:
            h = tcod.random.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
        if x is None:
            x = tcod.random.get_int(self.map.width - w - 1)
        if y is None:
            y = tcod.random.get_int(self.map.height - h - 1)

        utils.Rect.__init__(self, x, y, w, h)

    def populate(self):
        monster_count = tcod.random.get_int(const.MAX_ROOM_MONSTERS)

        for i in range(monster_count):
            x = tcod.random.get_int(self.x1, self.x2-1)
            y = tcod.random.get_int(self.y1, self.y2-1)

            if tcod.random.get_int(20) < 16:
                monster = EntityLiving(x, y, 'o', 'an orc', const.COLOR_ORC)
            else:
                monster = EntityLiving(x, y, 'T', 'a great Troll', const.COLOR_TROLL)

            if monster.can_pass(0, 0, self.map):
                self.map.add_entity(monster)

    def carve(self):
        for x in range(self.x1 + 1, self.x2 - 1):
            for y in range(self.y1 + 1, self.y2 - 1):
                self.map.tiles[x][y].pass_through = True
                self.map.tiles[x][y].see_through = True

    def __str__(self):
        return 'Room at ((%d, %d)-(%d, %d))' % (self.x1, self.y1, self.x2, self.y2)


class Entity:
    def __init__(self, x, y, char, name, color, blocks):
        self.map = None
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.on_move = []
        self.blocks = blocks
        self.attackable = False

    def can_pass(self, dx, dy, the_map=None):
        if not self.blocks: # non-blocking entities can pass through anything
            return True

        if the_map is None:
            the_map = self.map

        cell = the_map.tiles[self.x + dx][self.y + dy]
        if not cell.pass_through:
            return False

        for e in the_map.entities:
            if e.blocks and e.x == self.x + dx and e.y == self.y + dy:
                return False

        return True

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        if self.can_pass(dx, dy):
            self.x += dx
            self.y += dy

        for f in self.on_move:
            f(self)

    def draw(self, console):
        """ Draw self to the passed-in console """
        if self.map.is_visible(self.x, self.y):
            console.set_default_foreground(self.color)
            console.put_char(self.x, self.y, self.char)

    def clear(self, console):
        """ Remove self from the passed-in console """
        console.put_char(self.x, self.y, ' ')

    def __str__(self):
        return self.name

class EntityItem(Entity):
    def __init__(self, x, y, char, name, color):
        Entity.__init__(self, x, y, char, name, color, blocks=False)

class EntityLiving(Entity):
    def __init__(self, x, y, char, name, color):
        Entity.__init__(self, x, y, char, name, color, blocks=True)
        self.attackable = True

    def move(self, dx, dy):
        for e in self.map.entities:
            if e.attackable and e.x == self.x + dx and e.y == self.y + dy:
                self.attack(e)
                return

        Entity.move(self, dx, dy)

    def attack(self, target):
        print self.name.capitalize(), 'attacks', target.name, 'but deals no damage.'

    def taunt(self):
        if self.map.is_visible(self.x, self.y):
            print self.name.capitalize(), 'snorts in your general direction.'


class Map:
    def __init__(self, console):
        self.tiles = [[ Tile(False) for y in range(console.height)] for x in range(console.width)]
        self.rooms = []
        self.entities = []
        self.console = console
        self.fov_map = tcod.Map(console.width, console.height)
        self.width = console.width
        self.height = console.height
        self.fullbright = False

    def is_visible(self, x, y):
        if self.fullbright:
            return True
        else:
            return self.fov_map.is_in_fov(x, y)

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
            new_room = Room(self)
            new_room.generate()
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
                self.carve_h_tunnel(start_point.x, end_point.x, start_point.y)
                self.carve_v_tunnel(end_point.x, start_point.y, end_point.y)
            else:
                self.carve_v_tunnel(start_point.x, start_point.y, end_point.y)
                self.carve_h_tunnel(start_point.x, end_point.x, end_point.y)

    def populate_rooms(self):
        for i in range(1, len(self.rooms)):
            self.rooms[i].populate()

    def label_rooms(self):
        labels = utils.label_generator('A')
        for r in self.rooms:
            center = r.center()
            label = EntityItem(center.x, center.y, labels.next(), 'a room label', const.COLOR_LABEL)
            self.add_entity(label)

