#!/usr/bin/env python
import shelve

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
    elif key.c == ord('D'):
        print panel.messages

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
        elif key.c == ord('<') or key.c == ord('>'):
            if player.map.stairs.x == player.x and player.map.stairs.y == player.y:
                return const.ACTION_DESCEND_STAIRS
        elif key.c == ord('c'):
            utils.character_sheet(player)

    ents = player.map.entities_at(mouse.cx, mouse.cy, only_visible=True)
    if len(ents) > 0:
        names = ', '.join([e.name for e in ents])
        panel.status(names.capitalize(), tcod.COLOR_LIGHT_GRAY)
    else:
        panel.status('')

    return const.ACTION_NONE

def level_up_screen(player):
    choice = None
    while choice is None:
        choice = utils.menu('Level up! Choose a stat to raise:\n',
                      ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                       'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                       'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], 40)

        if choice.c == ord('a'): # more hp
            player.fighter.max_hp += 20
            player.fighter.hp += 20
        elif choice.c == ord('b'): # more power!
            player.fighter.power += 1
        elif choice.c == ord('c'):
            player.fighter.defense += 1
        else:
            choice = None # Try again

def recalc_fov(player, x, y):
    player.map.fov_map.compute_fov(player.x, player.y, const.FOV_RADIUS,
                            const.FOV_LIGHT_WALLS, const.FOV_ALGORITHM)

def player_attack(player, x, y):
    ents = player.map.entities_at(x, y)
    for e in ents:
        if e.fighter is not None and e != player:
            player.fighter.attack(e)

def player_look(player, x, y):
    ents = player.map.entities_at(player.x, player.y)
    ents.remove(player)
    if len(ents) > 0:
        names = ', '.join([e.name for e in ents])
        panel.add_message('You see here: ' + names, tcod.COLOR_LIGHT_LIME)

def player_death(player, killer):
    panel.add_message('You have died. Press Esc or q to quit.', tcod.COLOR_RED)
    player.char = '%'
    player.color = const.COLOR_REMAINS
    player.name = 'remains of ' + player.name
    player.map.fullbright = True

def player_kill(fighter, killed):
    player = fighter.owner
    if killed.fighter:
        fighter.xp += killed.fighter.xp
        panel.add_message('Gained %d XP.' % killed.fighter.xp, tcod.COLOR_ORANGE)

    if fighter.xp >= utils.xp_to_level_up(player.level):
        fighter.xp -= utils.xp_to_level_up(player.level)
        player.level += 1
        fighter.hp = fighter.max_hp
        panel.add_message('Your experience pushes you to a new plateau of battle skills. You are now level %d.' % player.level,
                          tcod.COLOR_YELLOW)
        level_up_screen(player)

def new_game():
    map = dungeon.Map(console)
    map.generate()
    #map.label_rooms()
    map.populate_rooms()

    spawn = map.rooms[0].center()
    player = entities.EntityLiving(spawn.x, spawn.y, '@', 'the adventurer', tcod.COLOR_WHITE,
                                   fighter=entities.Fighter(hp=100, defense=1, power=4,
                                                            on_death=player_death,
                                                            on_kill=player_kill))
    map.add_entity(player)
    map.player = player

    recalc_fov(player, 0, 0)
    player.on_move.append(recalc_fov)
    player.on_move.append(player_attack)
    player.on_move.append(player_look)

    panel.messages = []
    panel.add_message("Have fun, and enjoy your death!", tcod.COLOR_RED)
    return player

def next_level(player):
    panel.add_message("You take a moment to rest and recover your strength.", tcod.COLOR_LIGHT_VIOLET)
    player.fighter.heal(player.fighter.max_hp/2)

    panel.add_message('After a rare moment of peace, you descend further into the depths of the dungeon.', tcod.COLOR_RED)
    new_map = dungeon.Map(player.map.console, level=player.map.level+1)
    new_map.generate()
    new_map.populate_rooms()

    spawn = new_map.rooms[0].center()
    player.x = spawn.x
    player.y = spawn.y

    new_map.add_entity(player)
    new_map.player = player

    recalc_fov(player, 0, 0)

def save_game(map):
    s = shelve.open('savegame', 'n')
    s['map'] = map
    s['panel_messages'] = panel.messages
    s.close()

def load_game():
    s = shelve.open('savegame', 'r')
    map = s['map']
    panel.messages = s['panel_messages']
    s.close()

    map.init_fov()
    recalc_fov(map.player, 0, 0)
    return map.player

def game_loop(player):
    while not tcod.is_window_closed():
        utils.render_all(player)

        action = handle_events(player)
        if action == const.ACTION_EXIT:
            save_game(player.map)
            break
        elif action == const.ACTION_DESCEND_STAIRS:
            next_level(player)
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
        elif key.c == ord('b'): # Load game
            try:
                player = load_game()
                game_loop(player)
            except:
                utils.msgbox('Loading the game failed: are you sure one exists?')
                continue
        elif key.c == ord('c') or key.c == ord('q'): # Quit
            break;

tcod.set_custom_font('fonts/consolas12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
tcod.init_root(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, 'Random Life', False)
console = tcod.Console(const.MAP_WIDTH, const.MAP_HEIGHT)

libtcod.sys_set_fps(const.LIMIT_FPS)

if __name__ == '__main__':
    main_menu()
