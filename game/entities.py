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

    def draw(self, con):
        """ Draw self to the passed-in console """
        con.set_default_foreground(self.color)
        con.put_char(self.x, self.y, self.char)

    def clear(self, con):
        """ Remove self from the passed-in console """
        con.put_char(self.x, self.y, ' ')
