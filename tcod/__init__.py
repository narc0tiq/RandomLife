import libtcodpy as libtcod
from game import const

class Random:
    def __init__(self, stream_id):
        self.stream_id = stream_id

    def get_int(self, *args, **kwargs):
        """ rand.get_int([start,] stop) -> random integer

        Note the non-standard order of default arguments: if a single argument
        is provided, it is assumed to be the stop value, and the start (!) value
        then defaults to 0.

        You may also use keyword arguments start and stop if you prefer to be
        explicit -- this may be preferable to using the magic behaviour. Kwargs
        will override positional arguments.

        """
        if len(args) == 0 and 'stop' not in kwargs:
            raise TypeError('get_int expects either 1 positional argument or the keyword argument "stop"')

        min_value = max_value = 0
        if len(args) == 1:
            max_value = args[0]
        elif len(args) == 2:
            min_value = args[0]
            max_value = args[1]

        if 'start' in kwargs:
            min_value = kwargs['start']
        if 'stop' in kwargs:
            max_value = kwargs['stop']

        return libtcod.random_get_int(self.stream_id, min_value, max_value)

# A default Random for anyone to use
random = Random(0)

class Console:
    @staticmethod
    def set_custom_font(fontfile, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, horizontal_count=0, vertical_count=0):
        return libtcod.console_set_custom_font(fontfile, flags, horizontal_count, vertical_count)

    @staticmethod
    def init_root(width, height, title, fullscreen=False, renderer=libtcod.RENDERER_SDL):
        return libtcod.console_init_root(width, height, title, fullscreen, renderer)

    @staticmethod
    def wait_for_keypress(flush=False):
        return libtcod.console_wait_for_keypress(flush)

    @staticmethod
    def wait_for_event(mask, flush=False):
        key, mouse = (libtcod.Key(), libtcod.Mouse())
        libtcod.sys_wait_for_event(mask, key, mouse, flush)
        return (key, mouse)

    @staticmethod
    def set_fullscreen(want_fullscreen=True):
        return libtcod.console_set_fullscreen(want_fullscreen)

    @staticmethod
    def is_fullscreen():
        return libtcod.console_is_fullscreen()

    @staticmethod
    def is_key_pressed(key):
        return libtcod.console_is_key_pressed(key)

    @staticmethod
    def is_window_closed():
        return libtcod.console_is_window_closed()

    @staticmethod
    def flush():
        return libtcod.console_flush()

    # Root console has id 0
    ROOT_ID = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.console_id = libtcod.console_new(width, height)

    def __del__(self):
        libtcod.console_delete(self.console_id)

    def set_key_color(self, color):
        return libtcod.console_set_key_color(self.console_id, color)

    def blit(self, src_x=0, src_y=0, src_width=0, src_height=0,
             dest_console=None, dest_x=0, dest_y=0,
             alpha_fg=1.0, alpha_bg=1.0):
        if src_width == 0:
            src_width = self.width
        if src_height == 0:
            src_height = self.height

        dest_id = Console.ROOT_ID
        if dest_console is not None:
            dest_id = dest_console.console_id

        return libtcod.console_blit(self.console_id, src_x, src_y, src_width, src_height,
                             dest_id, dest_x, dest_y, alpha_fg, alpha_bg)

    def set_default_background(self, color):
        return libtcod.console_set_default_background(self.console_id, color)

    def set_default_foreground(self, color):
        return libtcod.console_set_default_foreground(self.console_id, color)

    def set_char_background(self, x, y, color, flags=libtcod.BKGND_SET):
        return libtcod.console_set_char_background(self.console_id, x, y, color, flags)

    def put_char(self, x, y, char, flags=libtcod.BKGND_NONE):
        return libtcod.console_put_char(self.console_id, x, y, char, flags)


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = libtcod.map_new(width, height)

    def set_properties(self, x, y, see_through, pass_through):
        return libtcod.map_set_properties(self.map, x, y, see_through, pass_through)

    def compute_fov(self, x, y, radius=const.FOV_RADIUS,
                    light_walls=const.FOV_LIGHT_WALLS, algorithm=const.FOV_ALGORITHM):
        return libtcod.map_compute_fov(self.map, x, y, radius, light_walls, algorithm)

    def is_in_fov(self, x, y):
        return libtcod.map_is_in_fov(self.map, x, y)
