#!/usr/bin/env python

from tcod import random, Console
from tcod import libtcodpy as libtcod

from game import const, dungeon, entities

def handle_keys(player):
    key, mouse = Console.wait_for_event(libtcod.EVENT_KEY_PRESS, flush=True)

    if(key.vk == libtcod.KEY_ENTER and key.lalt):
        Console.set_fullscreen(not Console.is_fullscreen())
    elif((key.vk == libtcod.KEY_ESCAPE) or (key.c == ord('q'))):
        return const.ACTION_EXIT
    elif key.c == ord('N'):
        player.blocks = not player.blocks
        print "Noclip set to ", not player.blocks
    elif key.c == ord('X'):
        player.map.fullbright = not player.map.fullbright

    if player.fighter.hp > 0:
        if(Console.is_key_pressed(libtcod.KEY_UP)):
            player.move(0, -1)
            return const.ACTION_MOVE
        elif(Console.is_key_pressed(libtcod.KEY_DOWN)):
            player.move(0, 1)
            return const.ACTION_MOVE
        elif(Console.is_key_pressed(libtcod.KEY_LEFT)):
            player.move(-1, 0)
            return const.ACTION_MOVE
        elif(Console.is_key_pressed(libtcod.KEY_RIGHT)):
            player.move(1, 0)
            return const.ACTION_MOVE

    return const.ACTION_NONE

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
    player = entities.EntityLiving(spawn.x, spawn.y, '@', 'the adventurer', libtcod.white,
                                  fighter=entities.Fighter(hp=30, defense=2, power=5))
    map.add_entity(player)
    map.player = player

    recalc_fov = lambda entity, unused_x, unused_y: map.fov_map.compute_fov(entity.x, entity.y)
    recalc_fov(player, 0, 0)
    player.on_move.append(recalc_fov)

    def player_attack(player, x, y):
        ents = map.entities_at(x, y)
        for e in ents:
            if e.fighter is not None and e != player:
                player.fighter.attack(e)
    player.on_move.append(player_attack)

    def player_look(player, x, y):
        ents = map.entities_at(player.x, player.y)
        ents.remove(player)
        if len(ents) > 0:
            print 'You see here:', ents
    player.on_move.append(player_look)

    def player_death(player):
        print 'You died. Press Esc or q to quit.'
        player.char = '%'
        player.color = const.COLOR_REMAINS
    player.fighter.on_death = player_death

    while not Console.is_window_closed():
        map.render()
        console.set_default_foreground(const.COLOR_GUI_FOREGROUND)
        console.print_ex(1, const.SCREEN_HEIGHT - 2, const.BACKGROUND_NONE, const.LEFT,
                         'HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp) + ' '*10)
        console.blit()
        Console.flush()
        map.post_render()

        action = handle_keys(player)
        if action == const.ACTION_EXIT:
            break
        elif action != const.ACTION_NONE:
            for e in map.entities:
                if e.ai is not None:
                    e.ai.think()

if(__name__ == "__main__"):
    void_main_of_silliness()
