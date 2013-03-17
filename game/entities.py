import math

import tcod
from game import const
from game.utils import panel

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
        self.fighter = None
        self.ai = None

    def can_pass(self, dx, dy, the_map=None):
        if the_map is None:
            the_map = self.map

        cell = the_map.tiles[self.x + dx][self.y + dy]
        if not cell.pass_through:
            return False

        for e in the_map.entities_at(self.x + dx, self.y + dy):
            if e.blocks:
                return False

        return True

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        if self.can_pass(dx, dy):
            self.x += dx
            self.y += dy

        for f in self.on_move:
            f(self, self.x + dx, self.y + dy)

    def move_towards(self, x, y):
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx**2 + dy**2)

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

    def __repr__(self):
        return self.name

class EntityItem(Entity):
    def __init__(self, x, y, char, name, color, item=None):
        Entity.__init__(self, x, y, char, name, color, blocks=False)

        self.item = item
        if item is not None:
            item.owner = self

    def remove_from_map(self):
        self.map.remove_entity(self)

class EntityLiving(Entity):
    def __init__(self, x, y, char, name, color, fighter=None, ai=None):
        Entity.__init__(self, x, y, char, name, color, blocks=True)

        self.fighter = fighter
        if fighter is not None:
            fighter.owner = self
        self.ai = ai
        if ai is not None:
            ai.owner = self

        self.inventory = []

    def can_pass(self, dx, dy, the_map=None):
        if not self.blocks: # non-blocking living entities can pass through anything
            return True

        return Entity.can_pass(self, dx, dy, the_map)

class Fighter:
    def __init__(self, hp, defense, power, on_death=None):
        self.max_hp = self.hp = hp
        self.defense = defense
        self.power = power
        self.on_death = on_death

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0 and self.on_death is not None:
            self.on_death(self.owner)

    def attack(self, target):
        if target.fighter is None:
            return # the target is unsuitable

        damage = self.power - target.fighter.defense

        if damage > 0:
            panel.add_message("%s attacks %s, doing %d damage!" % (
                                self.owner.name.capitalize(), target.name, damage))
            target.fighter.take_damage(damage)
        else:
            panel.add_message("%s attacks %s, but the attack is ineffective." % (
                                self.owner.name.capitalize(), target.name))

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster:
    def think(self):
        map = self.owner.map

        # if you can see it, it can see you:
        if not map.is_visible(self.owner.x, self.owner.y):
            return # nothing to do here, moving on.

        if self.owner.distance_to(map.player) >= 2:
            self.owner.move_towards(map.player.x, map.player.y)
        elif map.player.fighter.hp > 0:
            self.owner.fighter.attack(map.player)

class ConfusedMonster(BasicMonster):
    def __init__(self, old_ai, duration=const.CONFUSE_DURATION):
        self.old_ai = old_ai
        self.duration = duration

    def think(self):
        if self.duration > 0:
            self.owner.move(tcod.random.get_int(-1, 1), tcod.random.get_int(-1, 1))
            self.duration -= 1
        else:
            self.owner.ai = self.old_ai
            panel.add_message(self.owner.name.capitalize() + ' no longer seems confused.', tcod.COLOR_RED)

class Item:
    def __init__(self, on_use=None):
        self.on_use = on_use

    def pick_up(self, taker):
        if len(taker.inventory) >= 26:
            # HACK: taker is basically always going to be the player, so...
            panel.add_message('You cannot pick up ' + self.owner.name + ' because your inventory is full.', tcod.COLOR_RED)
        else:
            taker.inventory.append(self.owner)
            self.owner.remove_from_map()
            panel.add_message('You picked up ' + self.owner.name + '.', tcod.COLOR_GREEN)

    def use(self, user):
        if self.on_use is None:
            panel.add_message(self.owner.name.capitalize() + ' is unusable!', tcod.COLOR_RED)
        else:
            result = self.on_use(self, user) or const.ITEM_USE_DESTROY
            if result & const.ITEM_USE_DESTROY == const.ITEM_USE_DESTROY:
                user.inventory.remove(self.owner)
