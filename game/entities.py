class Entity:
    def __init__(self, x, y, char, color):
        self.map = None
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def can_pass(self, dx, dy):
        cell = self.map.tiles[self.x + dx][self.y + dy]
        return cell.pass_through

    def move(self, dx, dy):
        """ Move by dx in the X direction and by dy in the Y direction """
        if self.can_pass(dx, dy):
            self.x += dx
            self.y += dy

    def draw(self, console):
        """ Draw self to the passed-in console """
        console.set_default_foreground(self.color)
        console.put_char(self.x, self.y, self.char)

    def clear(self, console):
        """ Remove self from the passed-in console """
        console.put_char(self.x, self.y, ' ')
