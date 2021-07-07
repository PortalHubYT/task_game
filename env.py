from time import time, sleep
from copy import copy
from random import seed, shuffle, randint
from typing import Union
import os
import json
import re
import pytchat

import mc_api as mc

# These options let you restart the script while it's running with minimal redudance
INITIALIZE_SERVER = False
CLEAN_TERRAIN = False
PREPARE_GAMEMASTER = True
PREPARE_BOARD = True
GAME_LOOP = True

GAMEMASTER = "PortalHub"
GAMEMASTER_YAW = -180
GAMEMASTER_PITCH = 40
GAMEMASTER_HEIGHT = 200

BOARD_DISTANCE_SHIFT = 5
BOARD_DEPTH_SHIFT = 8
BOARD_SIZE = 13
BOARD_TEXTURE = mc.Block("smooth_quartz")

ROUND_TIME_SEC = 30

TASK_TEXT_DISTANCE_SHIFT = BOARD_DISTANCE_SHIFT + BOARD_SIZE + 50
TASK_TEXT_DEPTH_SHIFT = BOARD_DEPTH_SHIFT + 12
TASK_OVER_WAIT_TIME_SEC = 3

TASK_GOAL_PALETTE = ["polished_blackstone"]
TASK_SUCCESS_TEXT = "GG"
TASK_SUCCESS_PALETTE = ["purpur"]
TASK_FAILED_TEXT = "Better luck next time!"
TASK_FAILED_PALETTE = ["oak"]

ENTITY_MASTER_FILTER = [
    "area_effect_cloud",
    "ender_dragon",
    "experience_orb",
    "eye_of_ender",
    "falling_block",
    "firework_rocket",
    "item",
    "item_frame",
    "leash_knot",
    "llama_spit",
    "command_block_minecart",
    "painting",
    "ender_pearl",
    "experience_bottle",
    "wither",
    "player",
    "fishing_bobber",
    "vex",
    "giant",
    "tnt",
    "ghast",
    "shulker",
]

ENTITY_ACTION_FILTER = [
    "zoglin",
    "hoglin",
    "creeper",
    "tnt_minecart",
    "end_crystal",
    "dragon_fireball",
    "fireball",
]

BLOCK_MASTER_FILTER = ["tnt"]

CHAT_ID = "ZJTpX6oFyH8"


def get_value_list(value: str) -> list:
    """
    This function doesn't need to ever be called, it generates the
    constant declared after its scope.

    It stores and returns a list inside of them, and each (value below)
    can be accessed in its minecraft:namespace format as list items.
    Available values:
        - entity_type (= Entities)
        - block (= Blocks)
        - item (= Items)
    """

    path = os.path.dirname(os.path.abspath(__file__))
    actual_path = f"{path}/mc_api/setup/generated/reports/registries.json"

    with open(actual_path) as f:
        dictionnary = json.load(f)

    value_list = []
    for key in dictionnary[f"minecraft:{value}"]["entries"].keys():

        if value == "entity_type":
            if key.replace("minecraft:", "") in ENTITY_MASTER_FILTER:
                continue

        elif value == "block":
            if key.replace("minecraft:", "") in BLOCK_MASTER_FILTER:
                continue

        value_list.append(key)

    return value_list


BLOCK_LIST = get_value_list("block")
ENTITY_LIST = get_value_list("entity_type")
ITEM_LIST = get_value_list("item")
