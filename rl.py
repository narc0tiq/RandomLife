#!/usr/bin/env python

from modules import libtcodpy as libtcod
from modules.randomlife.entities import Entity
from modules.randomlife.tiles import Tile

LIMIT_FPS = 20

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)

def handle_keys(player):
    key = libtcod.console_wait_for_keypress(True)

    if(key.vk == libtcod.KEY_ENTER and key.lalt):
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif((key.vk == libtcod.KEY_ESCAPE) or (key.c == ord('q'))):
        return True

    if(libtcod.console_is_key_pressed(libtcod.KEY_UP)):
        player.move(0, -1)
    elif(libtcod.console_is_key_pressed(libtcod.KEY_DOWN)):
        player.move(0, 1)
    elif(libtcod.console_is_key_pressed(libtcod.KEY_LEFT)):
        player.move(-1, 0)
    elif(libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
        player.move(1, 0)

def make_map():
    global MAP_HEIGHT, MAP_WIDTH

    map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
    return map

def render_all(console, map, objects):
    global SCREEN_HEIGHT, SCREEN_WIDTH, COLOR_DARK_WALL, COLOR_DARK_GROUND

    for o in objects:
        o.draw(console)

    for x in range(len(map)):
        for y in range(len(map[x])):
            can_pass = map[x][y].pass_through
            if can_pass:
                libtcod.console_set_char_background(console, x, y, COLOR_DARK_WALL, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(console, x, y, COLOR_DARK_GROUND, libtcod.BKGND_SET)

            if not map[x][y].see_through:
                libtcod.console_set_char_background(console, x, y, libtcod.black, libtcod.BKGND_SET)

    libtcod.console_blit(console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_flush()

    for o in objects:
        o.clear(console)

def void_main_of_silliness():
    global SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS

    libtcod.console_set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Random Life', False)
    console = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    libtcod.sys_set_fps(LIMIT_FPS)

    map = make_map()
    map[30][22].pass_through = False
    map[30][22].see_through = map[40][22].pass_through = map[50][22].see_through = False

    player = Entity(map, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
    npc = Entity(map, SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2 - 5, '@', libtcod.yellow)
    objects = [npc, player]

    while not libtcod.console_is_window_closed():
        render_all(console, map, objects)

        if handle_keys(player):
            break



if(__name__ == "__main__"):
    void_main_of_silliness()
