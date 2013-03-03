#!/usr/bin/env python

from tcod import random, Console
from tcod import libtcodpy as libtcod

from game import const
from game import dungeon

def handle_keys(player):
    key, mouse = Console.wait_for_event(libtcod.EVENT_KEY_PRESS, flush=True)

    if(key.vk == libtcod.KEY_ENTER and key.lalt):
        Console.set_fullscreen(not Console.is_fullscreen())
    elif((key.vk == libtcod.KEY_ESCAPE) or (key.c == ord('q'))):
        return True
    elif key.c == ord('N'):
        player.blocks = not player.blocks
        print "Noclip set to ", not player.blocks
    elif key.c == ord('X'):
        player.map.fullbright = not player.map.fullbright

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

    map = dungeon.Map(console)
    map.generate()
    map.label_rooms()
    map.populate_rooms()

    spawn = map.rooms[0].center()
    player = dungeon.EntityLiving(spawn.x, spawn.y, '@', 'the adventurer', libtcod.white)
    map.add_entity(player)

    recalc_fov = lambda entity: map.fov_map.compute_fov(entity.x, entity.y)
    recalc_fov(player)
    player.on_move.append(recalc_fov)

    while not Console.is_window_closed():
        map.render()
        console.blit()
        Console.flush()
        map.post_render()

        if handle_keys(player): break

if(__name__ == "__main__"):
    void_main_of_silliness()
