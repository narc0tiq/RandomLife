
class Tile:
    def __init__(self, pass_through, see_through = None):
        self.pass_through = pass_through

        if(see_through is None):
            see_through = pass_through
        self.see_through = see_through

