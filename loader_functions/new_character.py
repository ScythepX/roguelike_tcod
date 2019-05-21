import tcod as libtcod

from components.fighter import Fighter
from components.level import Level
from components.inventory import Inventory
from components.equipments import Equipment, EquipmentSlots
from components.equippable import Equippable

from entity import Entity

from render_functions import RenderOrder


def new_player_character():
    warrior_max_hp = 150
    warrior_power = 3
    warrior_defense = 4

    thief_max_hp = 100
    thief_power = 4
    thief_defense = 1

    barbarian_max_hp = 200
    barbarian_power = 5
    barbarian_defense = 1

    characters = {
        'warrior': Fighter(warrior_max_hp, warrior_defense, warrior_power),
        'thief': Fighter(thief_max_hp, thief_defense, thief_power),
        'barbarian': Fighter(barbarian_max_hp, barbarian_defense, barbarian_power)
    }

    return characters


def new_player(name, color):
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()

    characters = new_player_character()

    if name == 'warrior':
        player = Entity(0, 0, color.get('player_tile'), libtcod.white, 'Warrior', blocks=True, render_order=RenderOrder.ACTOR,
                        fighter=characters.get('warrior'), inventory=inventory_component, level=level_component,
                        equipment=equipment_component)
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
        short_sword = Entity(0, 0, '|', libtcod.darker_sky, 'Short sword', equippable=equippable_component)
        player.inventory.add_item(short_sword)
        player.equipment.toggle_equip(short_sword)

        #return player

    elif name == 'thief':
        player = Entity(0, 0, color.get('player_tile'), libtcod.dark_green, 'Thief', blocks=True, render_order=RenderOrder.ACTOR,
                        fighter=characters.get('thief'), inventory=inventory_component, level=level_component,
                        equipment=equipment_component)
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
        dagger = Entity(0, 0, '-', libtcod.sky, 'Dagger', equippable=equippable_component)
        player.inventory.add_item(dagger)
        player.equipment.toggle_equip(dagger)

        #return player

    elif name == 'barbarian':
        player = Entity(0, 0, color.get('player_tile'), libtcod.red, 'Barbarian', blocks=True, render_order=RenderOrder.ACTOR,
                        fighter=characters.get('barbarian'), inventory=inventory_component, level=level_component,
                        equipment=equipment_component)
        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
        long_sword = Entity(0, 0, '/', libtcod.dark_red, 'Long sword', equippable=equippable_component)
        player.inventory.add_item(long_sword)
        player.equipment.toggle_equip(long_sword)

    return player
