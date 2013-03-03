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

def label_generator(char):
    ret = ord(char)
    while True:
        yield chr(ret)
        ret += 1

