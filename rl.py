#!/usr/bin/env python

import tcod
from tcod import libtcodpy as libtcod

from game import const, dungeon, entities
from game.utils import panel

def handle_events(player, map):
    key, mouse = tcod.check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE)

    if(key.vk == libtcod.KEY_ENTER and key.lalt):
        tcod.set_fullscreen(not tcod.is_fullscreen())
    elif((key.vk == libtcod.KEY_ESCAPE) or (key.c == ord('q'))):
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

    ents = map.entities_at(mouse.cx, mouse.cy, only_visible=True)
    if len(ents) > 0:
        names = ', '.join([e.name for e in ents])
        panel.status(names.capitalize(), tcod.COLOR_LIGHT_GRAY)
    else:
        panel.status('')

    return const.ACTION_NONE

def void_main_of_silliness():
    tcod.set_custom_font('fonts/dejavu12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    tcod.init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'Random Life', False)
    console = tcod.Console(const.MAP_WIDTH, const.MAP_HEIGHT)

    libtcod.sys_set_fps(const.LIMIT_FPS)

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
        panel.add_message('You died. Press Esc or q to quit.', tcod.COLOR_RED)
        player.char = '%'
        player.color = const.COLOR_REMAINS
        player.name = 'remains of ' + player.name
    player.fighter.on_death = player_death

    panel.add_message("Have fun, and enjoy your death!", tcod.COLOR_RED)

    while not tcod.is_window_closed():
        map.render()
        panel.clear(const.PANEL_BACKGROUND)
        panel.render_bar(1, 1, const.BAR_WIDTH, label='HP',
                         value=player.fighter.hp, maximum=player.fighter.max_hp,
                         bar_color=const.PANEL_BAR_COLOR, back_color=const.PANEL_BAR_BACK,
                         text_color=const.PANEL_TEXT_COLOR)

        console.blit()
        panel.render(tcod.root_console)
        tcod.flush()
        map.post_render()

        action = handle_events(player, map)
        if action == const.ACTION_EXIT:
            break
        elif action != const.ACTION_NONE:
            for e in map.entities:
                if e.ai is not None:
                    e.ai.think()

if(__name__ == "__main__"):
    void_main_of_silliness()
