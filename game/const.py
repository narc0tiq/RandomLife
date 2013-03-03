from tcod import libtcodpy as libtcod

LIMIT_FPS = 20

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
ROOM_COUNT = 30

FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 10

COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)
COLOR_LIGHT_WALL = libtcod.Color(130, 110, 50)
COLOR_LIGHT_GROUND = libtcod.Color(200, 180, 50)

COLOR_DARKNESS = libtcod.black
COLOR_LABEL = libtcod.blue

COLOR_ORC = libtcod.desaturated_green
COLOR_TROLL = libtcod.darker_green

MAX_ROOM_MONSTERS = 5
