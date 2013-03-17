#!/usr/bin/env python

import tcod
from tcod import libtcodpy as libtcod

from game import const, dungeon, entities, utils
panel = utils.panel

def handle_events(player):
    key, mouse = tcod.check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        tcod.set_fullscreen(not tcod.is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE or key.c == ord('q'):
        return const.ACTION_EXIT
    elif key.c == ord('N'):
        player.blocks = not player.blocks
        panel.add_message("Noclip set to " + str(not player.blocks), tcod.COLOR_LIGHT_FLAME)
    elif key.c == ord('X'):
        player.map.fullbright = not player.map.fullbright

    if player.fighter.hp > 0:
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player.move(0, -1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_KP9:
            player.move(1, -1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player.move(0, 1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_KP1:
            player.move(-1, 1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player.move(-1, 0)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_KP7:
            player.move(-1, -1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player.move(1, 0)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_KP3:
            player.move(1, 1)
            return const.ACTION_MOVE
        elif key.vk == libtcod.KEY_KP5 or key.c == ord('.'):
            # Wait
            return const.ACTION_MOVE
        elif key.c == ord('g'):
            for e in player.map.entities_at(player.x, player.y):
                if hasattr(e, 'item') and e.item is not None:
                    e.item.pick_up(player)
        elif key.c == ord('u'):
            item = utils.inventory_menu(player)
            if item:
                item.use(player)
        elif key.c == ord('d'):
            item = utils.inventory_menu(player)
            if item:
                item.drop(player)

    ents = player.map.entities_at(mouse.cx, mouse.cy, only_visible=True)
    if len(ents) > 0:
        names = ', '.join([e.name for e in ents])
        panel.status(names.capitalize(), tcod.COLOR_LIGHT_GRAY)
    else:
        panel.status('')

    return const.ACTION_NONE

def new_game():
    map = dungeon.Map(console)
    map.generate()
    map.label_rooms()
    map.populate_rooms()

    spawn = map.rooms[0].center()
    player = entities.EntityLiving(spawn.x, spawn.y, '@', 'the adventurer', tcod.COLOR_WHITE,
                                  fighter=entities.Fighter(hp=30, defense=2, power=5))
    map.add_entity(player)
    map.player = player

    def recalc_fov(player, x, y):
        map.fov_map.compute_fov(player.x, player.y, const.FOV_RADIUS,
                                const.FOV_LIGHT_WALLS, const.FOV_ALGORITHM)
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
            names = ', '.join([e.name for e in ents])
            panel.add_message('You see here: ' + names, tcod.COLOR_LIGHT_LIME)
    player.on_move.append(player_look)

    def player_death(player):
        panel.add_message('You have died. Press Esc or q to quit.', tcod.COLOR_RED)
        player.char = '%'
        player.color = const.COLOR_REMAINS
        player.name = 'remains of ' + player.name
    player.fighter.on_death = player_death

    panel.messages = []

    return player

def game_loop(player):
    panel.add_message("Have fun, and enjoy your death!", tcod.COLOR_RED)
    while not tcod.is_window_closed():
        utils.render_all(player)

        action = handle_events(player)
        if action == const.ACTION_EXIT:
            break
        elif action != const.ACTION_NONE:
            for e in player.map.entities:
                if e.ai is not None:
                    e.ai.think()

def main_menu():
    img = tcod.ImageFile("menu_background1.png")
    con = tcod.root_console

    while not tcod.is_window_closed():
        img.blit_2x(con)
        con.set_default_foreground(tcod.COLOR_LIGHT_YELLOW)
        con.print_ex(const.SCREEN_WIDTH/2, const.SCREEN_HEIGHT/2 - 4, align=tcod.ALIGN_CENTER,
                     text="Random Life")
        con.print_ex(const.SCREEN_WIDTH/2, const.SCREEN_HEIGHT-2, align=tcod.ALIGN_CENTER,
                     text="A tutorial roguelike using libtcod")

        key = utils.menu('', ['Start a new game', 'Resume last game', 'Quit'], width=24)

        if key.c == ord('a'): # New game
            game_loop(new_game())
        elif key.c == ord('c') or key.c == ord('q'): # Quit
            break;

tcod.set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
tcod.init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'Random Life', False)
console = tcod.Console(const.MAP_WIDTH, const.MAP_HEIGHT)

libtcod.sys_set_fps(const.LIMIT_FPS)

main_menu()
