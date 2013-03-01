#!/usr/bin/env python

from modules import libtcodpy as libtcod
from modules.randomlife.entities import Entity
from modules.randomlife.tiles import Tile
from modules.randomlife.dungeon import Room, carve_h_tunnel, carve_v_tunnel
from modules.randomlife.utils import label_generator

LIMIT_FPS = 20

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
ROOM_COUNT = 30

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
    global MAP_HEIGHT, MAP_WIDTH, ROOM_MIN_SIZE, ROOM_MAX_SIZE, ROOM_COUNT

    map = [[Tile(False) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    rooms = []
    for unused in range(ROOM_COUNT):
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Room(map, x, y, w, h)
        failed = False
        for other_room in rooms:
            if new_room.intersects(other_room):
                failed = True
                break
        if failed: continue

        rooms.append(new_room)

    for r in rooms:
        r.fill_room()

    for i in range(1, len(rooms)):
        start_point = rooms[i - 1].center()
        end_point = rooms[i].center()

        if libtcod.random_get_int(0, 0, 20) >= 12:
            carve_h_tunnel(map, start_point[0], end_point[0], start_point[1])
            carve_v_tunnel(map, end_point[0], start_point[1], end_point[1])
        else:
            carve_v_tunnel(map, start_point[0], start_point[1], end_point[1])
            carve_h_tunnel(map, start_point[0], end_point[0], end_point[1])

    return (map, rooms)

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

    map, rooms = make_map()

    spawn = rooms[0].center()
    entrance = Entity(map, spawn[0], spawn[1], '#', libtcod.green)
    player = Entity(map, spawn[0], spawn[1], '@', libtcod.white)
    npc = Entity(map, spawn[0], spawn[1] + 2, '@', libtcod.yellow)

    objects = []
    labels = label_generator('A')
    for r in rooms:
        center = r.center()
        label = Entity(map, center[0], center[1], labels.next(), libtcod.blue);
        objects.append(label)

    objects.extend([entrance, npc, player])

    while not libtcod.console_is_window_closed():
        render_all(console, map, objects)

        if handle_keys(player):
            break



if(__name__ == "__main__"):
    void_main_of_silliness()
