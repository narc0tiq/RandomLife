#!/usr/bin/env python

from tcod import Random, Console
from tcod import libtcodpy as libtcod

from game import const
from game.entities import Entity
from game.tiles import Tile
from game.dungeon import Room, carve_h_tunnel, carve_v_tunnel
from game.utils import label_generator

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

def make_map():
    map = [[Tile(False) for y in range(const.MAP_HEIGHT)] for x in range(const.MAP_WIDTH)]

    rand = Random(0)
    rooms = []
    for unused in range(const.ROOM_COUNT):
        w = rand.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
        h = rand.get_int(const.ROOM_MIN_SIZE, const.ROOM_MAX_SIZE)
        x = rand.get_int(const.MAP_WIDTH - w - 1)
        y = rand.get_int(const.MAP_HEIGHT - h - 1)

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

        if rand.get_int(20) >= 12:
            carve_h_tunnel(map, start_point[0], end_point[0], start_point[1])
            carve_v_tunnel(map, end_point[0], start_point[1], end_point[1])
        else:
            carve_v_tunnel(map, start_point[0], start_point[1], end_point[1])
            carve_h_tunnel(map, start_point[0], end_point[0], end_point[1])

    return (map, rooms)

def render_all(con, map, objects):
    for o in objects:
        o.draw(con)

    for x in range(len(map)):
        for y in range(len(map[x])):
            can_pass = map[x][y].pass_through
            if can_pass:
                con.set_char_background(x, y, const.COLOR_DARK_WALL)
            else:
                con.set_char_background(x, y, const.COLOR_DARK_GROUND)

            if not map[x][y].see_through:
                con.set_char_background(x, y, libtcod.black)

    con.blit()
    Console.flush()

    for o in objects:
        o.clear(con)

def void_main_of_silliness():
    Console.set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    Console.init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'Random Life', False)
    console = Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)

    libtcod.sys_set_fps(const.LIMIT_FPS)

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

    while not Console.is_window_closed():
        render_all(console, map, objects)

        if handle_keys(player):
            break


if(__name__ == "__main__"):
    void_main_of_silliness()
