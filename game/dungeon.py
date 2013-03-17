import tcod
from game import const, entities, utils
from game.utils import panel

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

def monster_death(monster):
    panel.add_message(monster.name.capitalize() + ' has been slain!', tcod.COLOR_ORANGE)
    monster.char = '%'
    monster.color = const.COLOR_REMAINS
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.map.entity_to_bottom(monster)

def use_health_potion(potion, user):
    if user.fighter.hp >= user.fighter.max_hp:
        # HACK: assuming user is always the player:
        panel.add_message('You are already as healthy as possible!', tcod.COLOR_RED)
        return const.ITEM_USE_CANCELLED

    panel.add_message('Your wounds mend themselves before your very eyes.', tcod.COLOR_LIGHT_VIOLET)
    user.fighter.heal(const.HEAL_AMOUNT)

def cast_lightning(scroll, user):
    target = user.map.find_nearest_shootable(user, const.LIGHTNING_RANGE)
    if target is None:
        panel.add_message('There are no monsters close enough to strike.', tcod.COLOR_RED)
        return const.ITEM_USE_CANCELLED

    panel.add_message('As you finish reading the words, you hear a loud thunderclap as lightning strikes ' +
                      target.name + '. It looks to have lost ' + str(const.LIGHTNING_DAMAGE) + ' HP.',
                      tcod.COLOR_LIGHT_BLUE)
    target.fighter.take_damage(const.LIGHTNING_DAMAGE)

def cast_confuse(scroll, user):
    target = user.map.find_nearest_shootable(user, const.CONFUSE_RANGE)
    if target is None:
        panel.add_message('There are no monsters close enough to strike.', tcod.COLOR_RED)
        return const.ITEM_USE_CANCELLED

    panel.add_message('You notice ' + target.name + ' suddenly stumble. It doesn\'t seem to be paying attention to you anymore.',
                      tcod.COLOR_LIGHT_GREEN)
    target.ai = entities.ConfusedMonster(target.ai)
    target.ai.owner = target

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
            x = tcod.random.get_int(self.x1+1, self.x2-1)
            y = tcod.random.get_int(self.y1+1, self.y2-1)

            if tcod.random.get_int(20) < 16:
                fighter = entities.Fighter(hp=10, defense=0, power=3, on_death=monster_death)
                ai = entities.BasicMonster()
                monster = entities.EntityLiving(x, y, 'o', 'an orc', const.COLOR_ORC, fighter=fighter, ai=ai)
            else:
                fighter = entities.Fighter(hp=14, defense=1, power=4, on_death=monster_death)
                ai = entities.BasicMonster()
                monster = entities.EntityLiving(x, y, 'T', 'a great troll', const.COLOR_TROLL, fighter=fighter, ai=ai)

            if monster.can_pass(0, 0, self.map):
                self.map.add_entity(monster)

        item_count = tcod.random.get_int(const.MAX_ROOM_ITEMS)
        for i in range(item_count):
            x = tcod.random.get_int(self.x1+1, self.x2-1)
            y = tcod.random.get_int(self.y1+1, self.y2-1)

            chance = tcod.random.get_int(100)
            if chance < 70:
                item_component = entities.Item(on_use=use_health_potion)
                item = entities.EntityItem(x, y, '!', 'a healing potion', tcod.COLOR_VIOLET, item=item_component)
            elif chance < 70+15:
                item_component = entities.Item(on_use=cast_lightning)
                item = entities.EntityItem(x, y, '#', 'a scroll of lightning bolt', tcod.COLOR_LIGHT_YELLOW, item=item_component)
            else:
                item_component = entities.Item(on_use=cast_confuse)
                item = entities.EntityItem(x, y, '#', 'a scroll of confuse', tcod.COLOR_LIGHT_LIME, item=item_component)

            if item.can_pass(0, 0, self.map):
                self.map.add_entity(item)
                self.map.entity_to_bottom(item)

    def carve(self):
        for x in range(self.x1 + 1, self.x2 - 1):
            for y in range(self.y1 + 1, self.y2 - 1):
                self.map.tiles[x][y].pass_through = True
                self.map.tiles[x][y].see_through = True

    def __str__(self):
        return 'Room at ((%d, %d)-(%d, %d))' % (self.x1, self.y1, self.x2, self.y2)


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
        self.player = None

    def is_visible(self, x, y):
        if self.fullbright:
            return True
        else:
            return self.fov_map.is_in_fov(x, y)

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.map = self

    def entity_to_bottom(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            self.entities.insert(0, entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.clear(self.console)

    def entities_at(self, x, y, only_visible=False):
        if only_visible and not self.is_visible(x, y):
            return []

        found = []
        for e in self.entities:
            if e.x == x and e.y == y:
                found.append(e)

        return found

    def find_nearest_shootable(self, entity, max_range):
        nearest_target = None
        nearest_dist = max_range + 1

        for e in self.entities:
            if e.fighter and not e == entity and self.is_visible(e.x, e.y):
                dist = entity.distance_to(e)
                if dist < nearest_dist:
                    nearest_target = e
                    nearest_dist = dist

        return nearest_target

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
            label = entities.EntityItem(center.x, center.y, labels.next(), 'a room label', const.COLOR_LABEL)
            self.add_entity(label)

