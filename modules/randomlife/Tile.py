from modules import libtcodpy as libtcod

class Tile:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        self.x += dx
        self.y += dy

    def draw(self, console):
        """ Draw self to the passed-in console """
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, console):
        """ Remove self from the passed-in console """
        libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)
