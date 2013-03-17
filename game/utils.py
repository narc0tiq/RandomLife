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

