class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w + 1 # compensate for range(a, b) excluding b
        self.y1 = y
        self.y2 = y + h + 1 # same as above
