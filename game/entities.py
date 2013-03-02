from tcod import libtcodpy as libtcod

class Entity:
    def __init__(self, map, x, y, char, color):
        self.map = map
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def can_pass(self, dx, dy):
        cell = self.map[self.x + dx][self.y + dy]
        return cell.pass_through

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        if self.can_pass(dx, dy):
            self.x += dx
            self.y += dy

    def draw(self, console):
        """ Draw self to the passed-in console """
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, console):
        """ Remove self from the passed-in console """
        libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)
