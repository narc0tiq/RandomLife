from math import ceil
import textwrap

import tcod

from game import const

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w + 1 # compensate for range(a, b) excluding b
        self.y1 = y
        self.y2 = y + h + 1 # same as above

    def center(self):
        center = Point()
        center.x = (self.x1 + self.x2) / 2
        center.y = (self.y1 + self.y2) / 2

        return center

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class GUIPanel:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.console = tcod.Console(width, height)
        self.messages = []
        self.status_message = ('', tcod.COLOR_BLACK)

    def clear(self, color):
        self.console.set_default_background(color)
        self.console.clear()

    def render_bar(self, x, y, width, label, value, maximum, bar_color, back_color, text_color=tcod.COLOR_WHITE):
        bar_width = int(ceil(float(value * width) / maximum))

        self.console.set_default_background(back_color)
        self.console.rect(x, y, width, height=1, clear=True, effect=tcod.BACKGROUND_SCREEN)

        self.console.set_default_background(bar_color)
        if bar_width > 0:
            self.console.rect(x, y, bar_width, height=1, effect=tcod.BACKGROUND_SCREEN)

        self.console.set_default_foreground(text_color)
        self.console.print_ex(x + (width / 2), y, tcod.BACKGROUND_NONE, tcod.ALIGN_CENTER,
                              "%s: %d/%d" % (label, value, maximum))

    def add_message(self, text, color=tcod.COLOR_WHITE):
        lines = textwrap.wrap(text, const.MSG_WIDTH)

        for line in lines:
            if len(self.messages) >= const.MSG_HEIGHT:
                del self.messages[0]

            self.messages.append((line, color))

    def status(self, text, color=tcod.COLOR_WHITE):
        self.status_message = (text, color)

    def render(self, dest_console, x=None, y=None):
        message_y = 1
        for line, color in self.messages:
            self.console.set_default_foreground(color)
            self.console.print_ex(const.PANEL_MSG_X, message_y, text=line)
            message_y += 1

        line, color = self.status_message
        self.console.set_default_foreground(color)
        self.console.print_ex(1, 0, tcod.BACKGROUND_NONE, tcod.ALIGN_LEFT, line)

        if x is None:
            x = self.x
        if y is None:
            y = self.y
        self.console.blit(0, 0, dest_console=dest_console, dest_x=x, dest_y=y)


panel = GUIPanel(0, const.PANEL_Y, const.SCREEN_WIDTH, const.PANEL_HEIGHT)

def label_generator(char):
    ret = ord(char)
    while True:
        yield chr(ret)
        ret += 1

def xp_to_level_up(level=1):
    return const.LEVEL_UP_BASE + (level * const.LEVEL_UP_INCREMENT)

def menu(header, options, width):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options!')

    header_height = 0
    if len(header) > 0:
        header_height = tcod.root_console.get_height_rect(width=width, text=header)
    height = header_height + len(options)

    con = tcod.Console(width, height)
    con.set_default_foreground(tcod.COLOR_WHITE)
    con.print_rect_ex(text=header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '( ) ' + option_text
        con.set_default_foreground(tcod.COLOR_WHITE)
        con.print_ex(y=y, text=text)
        con.set_default_foreground(tcod.COLOR_YELLOW)
        con.put_char(1, y, chr(letter_index))
        y += 1
        letter_index += 1

    x = const.SCREEN_WIDTH/2 - width/2
    y = const.SCREEN_HEIGHT/2 - height/2
    con.blit(dest_x=x, dest_y=y, alpha_bg=0.7)

    tcod.flush()
    key, mouse = tcod.wait_for_event(tcod.EVENT_KEY_PRESS, flush=True)
    return key

def inventory_menu(player):
    if len(player.inventory) == 0:
        panel.add_message('You can\'t use anything -- you don\'t have anything!', tcod.COLOR_RED)
        return

    options = [item.name for item in player.inventory]
    key = menu('Use what (Esc to back out)?', options, const.INVENTORY_WIDTH)

    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return player.inventory[index].item

def msgbox(text, width=50):
    menu("\n\n%s\n\n"%text, [], width)

def msgbox_ml(lines, width=50):
    msgbox('\n'.join(lines), width)

def render_all(player):
    player.map.render()
    panel.clear(const.PANEL_BACKGROUND)
    panel.render_bar(1, 1, const.BAR_WIDTH, label='HP',
                     value=player.fighter.hp, maximum=player.fighter.max_hp,
                     bar_color=const.PANEL_HPBAR_COLOR, back_color=const.PANEL_HPBAR_BACK,
                     text_color=const.PANEL_TEXT_COLOR)
    panel.render_bar(1, 2, const.BAR_WIDTH, label='XP',
                     value=player.fighter.xp, maximum=xp_to_level_up(player.level),
                     bar_color=const.PANEL_XPBAR_COLOR, back_color=const.PANEL_XPBAR_BACK,
                     text_color=const.PANEL_TEXT_COLOR)

    panel.console.set_default_foreground(tcod.COLOR_YELLOW)
    panel.console.print_ex(x=1, y=6, text='Dungeon(%d)' % player.map.level)

    player.map.console.blit()
    panel.render(tcod.root_console)
    tcod.flush()
    player.map.post_render()

def target_tile(player, max_range=None):
    while True:
        tcod.flush()
        key, mouse = tcod.check_for_event()
        render_all(player)

        x, y = (mouse.cx, mouse.cy)
        if mouse.rbutton_pressed or key.vk == tcod.KEY_ESCAPE:
            panel.add_message('Cancelled.', tcod.COLOR_RED)
            return (None, None)
        elif(mouse.lbutton_pressed and player.map.is_visible(x, y) and
             (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(player, max_range=None):
    while True:
        x, y = target_tile(player, max_range)
        if x is None:
            return None

        for e in player.map.targets_at(x, y, only_visible=True):
            if e != player:
                return e

def character_sheet(player):
    msgbox_ml(['Character information', '',
               'Level: %d' % player.level,
               'Experience: %d (%d to level up)' % (player.fighter.xp, xp_to_level_up(player.level)),
               'Constitution (max HP): %d' % player.fighter.max_hp,
               'Strength (attack): %d' % player.fighter.power,
               'Agility (defense): %d' % player.fighter.defense], 40)

def random_choice_index(options):
    max_roll = sum(options)
    if(max_roll <= 0):
        raise ValueError('Trying to pick between %d options!' % max_roll)

    die_roll = tcod.random.get_int(sum(options))

    for i in range(len(options)):
        if options[i] == 0:
            continue # Chance of 0 means it won't happen!

        if die_roll <= options[i]:
            return i
        else:
            die_roll -= options[i]

def random_choice(options_dict):
    """
    An options_dict looks like this {option1: 10, option2: 15}, where the keys
    are the options, and the values are their chance of occurring.
    In the example above, option1 has a 10/25 chance and option2 has a 15/25
    chance.
    """

    options = options_dict.keys()
    return options[random_choice_index(options_dict.values())]

def from_level(levels_dict, level=1):
    """
    A levels_dict looks like {1: 10, 4: 12}, where the keys are the level, and
    the values are the value to be returned for that level or those above
    (unless a higher-level value exists).
    In the example above, for level 1-3 the returned value would be 10, and for
    levels 4 and above the returned value would be 12.
    """

    for l in reversed(levels_dict.keys()):
        if l <= level:
            return levels_dict[l]

    return 0

