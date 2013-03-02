#!/usr/bin/env python

from tcod import random, Console
from tcod import libtcodpy as libtcod

from game import const
from game.dungeon import Map
from game.entities import Entity

def handle_keys(player):
    key = Console.wait_for_keypress(True)

    if(key.vk == libtcod.KEY_ENTER and key.lalt):
        Console.set_fullscreen(not Console.is_fullscreen())
    elif((key.vk == libtcod.KEY_ESCAPE) or (key.c == ord('q'))):
        return True

    if(Console.is_key_pressed(libtcod.KEY_UP)):
        player.move(0, -1)
    elif(Console.is_key_pressed(libtcod.KEY_DOWN)):
        player.move(0, 1)
    elif(Console.is_key_pressed(libtcod.KEY_LEFT)):
        player.move(-1, 0)
    elif(Console.is_key_pressed(libtcod.KEY_RIGHT)):
        player.move(1, 0)

def void_main_of_silliness():
    Console.set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    Console.init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'Random Life', False)
    console = Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

    libtcod.sys_set_fps(const.LIMIT_FPS)

    map = Map(console)
    map.generate()
    map.label_rooms()

    spawn = map.rooms[0].center()
    entrance = Entity(spawn[0], spawn[1], '#', libtcod.green)
    player = Entity(spawn[0], spawn[1], '@', libtcod.white)
    npc = Entity(spawn[0], spawn[1] + 2, '@', libtcod.yellow)

    map.add_entity(entrance)
    map.add_entity(player)
    map.add_entity(npc)

    while not Console.is_window_closed():
        map.render()
        console.blit()
        Console.flush()
        map.post_render()

        if handle_keys(player): break

if(__name__ == "__main__"):
    void_main_of_silliness()
