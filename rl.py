#!/usr/bin/env python

from modules import libtcodpy as libtcod
from modules.randomlife.Tile import Tile

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

playerx = SCREEN_WIDTH / 2
playery = SCREEN_HEIGHT / 2

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

def void_main_of_silliness():
    global SCREEN_WIDTH, SCREEN_HEIGHT, LIMIT_FPS

    libtcod.console_set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Random Life', False)
    con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    libtcod.sys_set_fps(LIMIT_FPS)

    player = Tile(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
    npc = Tile(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2 - 5, '@', libtcod.yellow)

    objects = [npc, player]
    while not libtcod.console_is_window_closed():
        for o in objects:
            o.draw(con)

        libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        libtcod.console_flush()

        player.clear(con)
        exit = handle_keys(player)
        if(exit): break



if(__name__ == "__main__"):
    void_main_of_silliness()
