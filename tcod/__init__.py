import libtcodpy as libtcod

class Random:
    @staticmethod
    def get_int(stream_id, min_value=None, max_value=None):
        """WARNING: Non-standard default arguments! If called with a single
        parameter, or two parameters, this function will assume they are
        either max_value, or min_value and max_value, respectively.

        To avoid confusion, ALWAYS provide both min_value and max_value
        if you want to provide the stream_id.

        """
        if min_value is None: # One argument, assume it's max_value
            stream_id, min_value, max_value = (0, 0, stream_id)
        elif max_value is None: # Two arguments, assume neither is stream_id
            stream_id, min_value, max_value = (0, stream_id, min_value)

        return libtcod.random_get_int(stream_id, min_value, max_value)


class Console:
    @staticmethod
    def set_custom_font(fontfile, flags=libtcod.FONT_LAYOUT_ASCII_INCOL, horizontal_count=0, vertical_count=0):
        return libtcod.console_set_custom_font(fontfile, flags, horizontal_count, vertical_count)

    @staticmethod
    def init_root(width, height, title, fullscreen=False, renderer=libtcod.RENDERER_SDL):
        return libtcod.console_init_root(width, height, title, fullscreen, renderer)

    @staticmethod
    def wait_for_keypress(flush):
        return libtcod.console_wait_for_keypress(flush)

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

