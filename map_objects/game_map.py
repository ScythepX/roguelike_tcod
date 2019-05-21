import tcod as libtcod
from random import randrange, choice

from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from components.equipments import EquipmentSlots
from components.equippable import Equippable

from render_functions import RenderOrder

from entity import Entity
from components.stairs import Stairs

from game_messages import Message

from item_functions import heal, cast_lighting, cast_fireball, cast_confuse

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from map_objects.bsp_constants import BspConstants

from random_utils import from_dungeon_level, random_choice_from_dict


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.bsp_rooms = []

        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, player, entities, color, max_rooms=None, room_min_size=None, room_max_size=None, map_width=None, map_height=None):
        '''rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.interset(other_room):
                    break
            else:
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    if randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, prev_y)

                self.place_entities(new_room, entities)

                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)
        '''

        bsp = libtcod.bsp_new_with_size(0, 0, self.width, self.height)

        libtcod.bsp_split_recursive(bsp, 0, BspConstants.DEPTH, BspConstants.MIN_SIZE + 1,
                                    BspConstants.MIN_SIZE + 1, 2, 2)
        libtcod.bsp_traverse_inverted_level_order(bsp, self.travers_node)

        stairs_location = choice(self.bsp_rooms)
        x = stairs_location[0]
        y = stairs_location[1]
        stairs_component = Stairs(self.dungeon_level + 1)
        self.bsp_rooms.remove(stairs_location)
        stairs = Entity(x, y, '<', libtcod.white, 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(stairs)

        player_room = choice(self.bsp_rooms)
        self.bsp_rooms.remove(player_room)
        player.x = player_room[0]
        player.y = player_room[1]

        for room in self.bsp_rooms:
            new_room = Rect(room[0], room[1], 2, 2)
            self.place_entities(new_room, entities, color)

    def travers_node(self, node, dat):
        if libtcod.bsp_is_leaf(node):
            minx = node.x + 1
            maxx = node.x + node.w - 1
            miny = node.y + 1
            maxy = node.y + node.h - 1

            if maxx == self.width - 1:
                maxx -= 1
            if maxy == self.height - 1:
                maxy -= 1

            if BspConstants.FULL_ROOMS == False:
                minx = libtcod.random_get_int(None, minx, maxx - BspConstants.MIN_SIZE + 1)
                miny = libtcod.random_get_int(None, miny, maxy - BspConstants.MIN_SIZE + 1)
                maxx = libtcod.random_get_int(None, minx + BspConstants.MIN_SIZE - 2, maxx)
                maxy = libtcod.random_get_int(None, miny + BspConstants.MIN_SIZE - 2, maxy)

            node.x = minx
            node.y = miny
            node.w = maxx - minx + 1
            node.h = maxy - miny + 1

            for x in range(minx, maxx + 1):
                for y in range(miny, maxy + 1):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False

            self.bsp_rooms.append((int((minx + maxx) / 2), int((miny + maxy) / 2)))

        else:
            left = libtcod.bsp_left(node)
            right = libtcod.bsp_right(node)
            node.x = min(left.x, right.x)
            node.y = min(left.y, right.y)
            node.w = max(left.x + left.w, right.x + right.w) - node.x
            node.h = max(left.y + left.h, right.y + right.h) - node.y

            if node.horizontal:
                if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                    x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
                    x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
                    y = libtcod.random_get_int(None, left.y + left.h, right.y)
                    self.vline_up(x1, y - 1)
                    self.hline(x1, y, x2)
                    self.vline_down(x2, y + 1)

                else:
                    minx = max(left.x, right.x)
                    maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                    x = libtcod.random_get_int(None, minx, maxx)

                    while x > self.width - 1:
                        x -= 1

                    self.vline_down(x, right.x)
                    self.vline_up(x, right.y - 1)
            else:
                if left.x + left.h - 1 < right.y or right.x + right.h - 1 < left.y:
                    y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                    y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                    x = libtcod.random_get_int(None, left.x + left.w, right.x)
                    self.hline_left(x - 1, y1)
                    self.vline(x, y1, y2)
                    self.hline_right(x + 1, y2)
                else:
                    miny = max(left.y, right.y)
                    maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                    y = libtcod.random_get_int(None, miny, maxy)

                    while y > self.height - 1:
                        y -= 1

                    self.hline_left(right.x - 1, y)
                    self.hline_right(right.x, y)
        return True

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def vline(self, x, y1, y2):
        if y1 > y2:
            y1, y2 = y2, y1

        for y in range(y1, y2 + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def vline_up(self, x, y):
        while y >= 0 and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y -= 1

    def vline_down(self, x, y):
        while y < self.height and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y += 1

    def hline(self, x1, y, x2):
        if x1 > x2:
            x1, x2 = x2, x1

        for x in range(x1, x2 + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def hline_left(self, x, y):
        while x >= 0 and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x -= 1

    def hline_right(self, x, y):
        while x < self.width and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x += 1

    def place_entities(self, room, entities, color):
        number_of_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        number_of_items = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }

        item_chances = {
            'healing_poition': 70,
            'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
            'lighting_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            #x = randrange(int(room.x1 + 1), int(room.x2 - 1), 1)
            #y = randrange(int(room.y1 + 1), int(room.y2 - 1), 1)
            x = libtcod.random_get_int(None, int(room.x1), int(room.x2))
            y = libtcod.random_get_int(None, int(room.y1), int(room.y2))

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'orc':
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()

                    monster = Entity(x, y, 'o', libtcod.green, 'Orc', blocks=True,
                                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                else:
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()

                    monster = Entity(x, y, 'T', libtcod.white, 'Troll', blocks=True, fighter=fighter_component,
                                     render_order=RenderOrder.ACTOR, ai=ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            x = libtcod.random_get_int(0, int(room.x1), int(room.x2))
            y = libtcod.random_get_int(0, int(room.y1), int(room.y2))

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_poition':
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == 'sword':
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x, y, '/', libtcod.white, 'Sword', equippable=equippable_component)

                elif item_choice == 'shield':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, '[', libtcod.white, 'Shield', equippable=equippable_component)

                elif item_choice == 'fireball_scroll':
                    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                          damage=25, radius=3)
                    item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)

                elif item_choice == 'confusion_scroll':
                    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancle.', libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)

                else:
                    item_component = Item(use_function=cast_lighting, damage=40, maximum_range=5)
                    item = Entity(x, y, '#', libtcod.yellow, 'Lighting Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)

                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[int(x)][int(y)].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(player, entities, constants['colors'])

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities
