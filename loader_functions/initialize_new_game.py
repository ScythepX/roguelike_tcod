import tcod as libtcod

from loader_functions.new_character import new_player

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap


def get_constants():
    window_title = 'Roguelike Game'

    screen_width = 80
    screen_height = 40

    bar_width = 10
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 5
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 33

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    '''colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }'''

    colors = {
        'wall_tile': 256,
        'floor_tile': 257,
        'player_tile': 258,
        'orc_tile': 259,
        'troll_tile': 260,
        'scroll_tile': 261,
        'healpoition_tile': 262,
        'sword_tile': 263,
        'shield_tile': 264,
        'stairsdown_tile': 265,
        'dagger_tile': 266
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors
    }

    return constants


def get_game_variables(constants, name_character):
    player = new_player(name_character, constants['colors'])
    entities = [player]

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(player, entities, constants['colors'])

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, game_map, message_log, game_state
