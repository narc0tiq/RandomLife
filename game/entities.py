import math

import tcod
from game import const, utils
panel = utils.panel

class Entity:
    def __init__(self, x, y, char, name, color, level=1, blocks=False, always_visible=False):
        self.map = None
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.on_move = []
        self.level = level
        self.blocks = blocks
        self.always_visible = always_visible
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

    def distance(self, x, y):
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def draw(self, console):
        """ Draw self to the passed-in console """
        if((self.always_visible and self.map.is_explored(self.x, self.y)) or
           self.map.is_visible(self.x, self.y)):
            console.set_default_foreground(self.color)
            console.put_char(self.x, self.y, self.char)

    def clear(self, console):
        """ Remove self from the passed-in console """
        console.put_char(self.x, self.y, ' ')

class EntityItem(Entity):
    def __init__(self, x, y, char, name, color, item=None):
        Entity.__init__(self, x, y, char, name, color, always_visible=True)

        self.item = item
        if item is not None:
            item.owner = self

    def remove_from_map(self):
        self.map.remove_entity(self)
        self.map = None

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
    def __init__(self, hp, defense, power, xp=0, on_death=None, on_kill=None):
        self.max_hp = self.hp = hp
        self.defense = defense
        self.power = power
        self.xp = xp
        self.on_death = on_death
        self.on_kill = on_kill

    def take_damage(self, damage, damage_source=None):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0 and self.on_death is not None:
            if(damage_source is not None and hasattr(damage_source, 'on_kill') and
               damage_source.on_kill is not None):
                damage_source.on_kill(damage_source, self.owner)
            self.on_death(self.owner, damage_source)

    def attack(self, target):
        if target.fighter is None:
            return # the target is unsuitable

        damage = self.power - target.fighter.defense

        if damage > 0:
            panel.add_message("%s attacks %s, doing %d damage!" % (
                                self.owner.name.capitalize(), target.name, damage))
            target.fighter.take_damage(damage, self)
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

    def drop(self, dropper):
        dropper.map.add_entity(self.owner)
        dropper.map.entity_to_bottom(self.owner)
        dropper.inventory.remove(self.owner)
        self.owner.x = dropper.x
        self.owner.y = dropper.y
        panel.add_message('You drop ' + self.owner.name + '.', tcod.COLOR_YELLOW)

    def use(self, user):
        if self.on_use is None:
            panel.add_message(self.owner.name.capitalize() + ' is unusable!', tcod.COLOR_RED)
        else:
            result = self.on_use(self, user) or const.ITEM_USE_DESTROY
            if result & const.ITEM_USE_DESTROY == const.ITEM_USE_DESTROY:
                user.inventory.remove(self.owner)

def monster_death(monster, killer):
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
    panel.add_message('Left-click a monster to confuse, or right-click to cancel.', tcod.COLOR_LIGHT_CYAN)
    target = utils.target_monster(user, const.CONFUSE_RANGE)
    if target is None:
        return const.ITEM_USE_CANCELLED

    panel.add_message('You notice ' + target.name + ' suddenly stumble. It doesn\'t seem to be paying attention to you anymore.',
                      tcod.COLOR_LIGHT_GREEN)
    target.ai = ConfusedMonster(target.ai)
    target.ai.owner = target

def cast_fireball(scroll, user):
    panel.add_message('Left-click a target tile for the fireball, or right-click to cancel.', tcod.COLOR_LIGHT_CYAN)
    x, y = utils.target_tile(user)
    if x is None:
        return const.ITEM_USE_CANCELLED

    panel.add_message('A ball of fire appears in front of your pointing finger as you finish reading the scroll, ' +
                      'and flies to the indicated location before exploding.', tcod.COLOR_FLAME)

    targets = user.map.targets_near(x, y, const.FIREBALL_RADIUS)
    if len(targets) == 0: # No targets? Tough luck.
        return const.ITEM_USE_DESTROY

    targets_string = ', '.join([t.name for t in targets]).capitalize()
    if len(targets) == 1:
        targets_string += ' is'
    else:
        targets_string += ' are all'
    panel.add_message(targets_string + ' burned for ' + str(const.FIREBALL_DAMAGE) + ' HP.', tcod.COLOR_ORANGE)

    for t in targets:
        t.fighter.take_damage(const.FIREBALL_DAMAGE)

def make_orc(x, y):
    fighter = Fighter(hp=20, defense=0, power=4, xp=35, on_death=monster_death)
    ai = BasicMonster()
    return EntityLiving(x, y, 'o', 'an orc', const.COLOR_ORC, fighter=fighter, ai=ai)

def make_troll(x, y):
    fighter = Fighter(hp=30, defense=2, power=8, xp=100, on_death=monster_death)
    ai = BasicMonster()
    return EntityLiving(x, y, 'T', 'a great troll', const.COLOR_TROLL, fighter=fighter, ai=ai)

def make_health_potion(x, y):
    item_component = Item(on_use=use_health_potion)
    return EntityItem(x, y, '!', 'a healing potion', tcod.COLOR_VIOLET, item=item_component)

def make_lightning_scroll(x, y):
    item_component = Item(on_use=cast_lightning)
    return EntityItem(x, y, '#', 'a scroll of lightning bolt', tcod.COLOR_LIGHT_YELLOW, item=item_component)

def make_confuse_scroll(x, y):
    item_component = Item(on_use=cast_confuse)
    return EntityItem(x, y, '#', 'a scroll of confuse', tcod.COLOR_LIGHT_LIME, item=item_component)

def make_fireball_scroll(x, y):
    item_component = Item(on_use=cast_fireball)
    return EntityItem(x, y, '#', 'a scroll of fireball', tcod.COLOR_FLAME, item=item_component)

