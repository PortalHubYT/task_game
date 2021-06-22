from time import time, sleep
from copy import copy
from random import seed, shuffle, randint
from typing import Union
import os
import json
import re
import pytchat

import mc_api as mc

# TODO: Add a barrier wall in front of the player
# TODO: Reagit@github.com:PortalHubYT/mc_api.gitd and store message in async, yield them to the gameloop and clean up the queue each tasks #funyrom?
# TODO: Find a final and durable solution for the command blocks in-game

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


def get_entity_pos(entity_name) -> mc.BlockCoordinates:
    coords = mc.post(f"data get entity @e[type={entity_name}, limit=1, sort=nearest]")

    coords = coords[coords.find("Pos") :]
    coords = coords[: coords.find("]")]
    coords = coords[coords.find("[") + 1 :]
    coords = coords.split(",")

    try:
        x = float(coords[0][:-1])
        y = float(coords[1][:-1])
        z = float(coords[2][:-1])
    except ValueError:
        x = 0.0
        y = 0.0
        z = 0.0

    return mc.BlockCoordinates(x, y, z)


def get_gamemaster_pos() -> mc.BlockCoordinates:
    coords = mc.post(f"data get entity {GAMEMASTER}")

    coords = coords[coords.find("Pos") :]
    coords = coords[: coords.find("]")]
    coords = coords[coords.find("[") + 1 :]
    coords = coords.split(",")

    try:
        x = float(coords[0][:-1])
        y = float(coords[1][:-1])
        z = float(coords[2][:-1])
    except ValueError:
        x = 0.0
        y = 0.0
        z = 0.0

    return mc.BlockCoordinates(x, y, z)


def foo_task():
    print("This task is not implemented yet")


def get_board_zone() -> mc.Zone:
    player_pos = get_gamemaster_pos()

    board_pos1 = copy(player_pos)

    board_pos1.x -= BOARD_SIZE / 2
    board_pos1.y -= BOARD_DEPTH_SHIFT
    board_pos1.z -= BOARD_DISTANCE_SHIFT

    board_pos2 = copy(board_pos1)

    board_pos2.x += BOARD_SIZE - 1
    board_pos2.z -= BOARD_SIZE - 1

    return mc.Zone(board_pos1, board_pos2)


def get_board_play_zone() -> mc.Zone:
    coords = get_board_zone()
    coords.pos1.y += 1
    coords.pos2.y += 1

    return coords


def get_random_cell_on_board() -> mc.BlockCoordinates:
    coords = get_board_zone()

    random_x = randint(int(coords.pos1.x), int(coords.pos2.x))
    random_z = randint(int(coords.pos2.z), int(coords.pos1.z) - 1)
    random_y = coords.pos1.y + 1

    return mc.BlockCoordinates(random_x, random_y, random_z)


def task_kill_the_entity(action: str, instructions: dict = None) -> Union[dict, bool]:

    if action == "run":

        instructions = {}

        random_coords = get_random_cell_on_board()

        filter = [
            "fireball",
            "dragon_fireball",
            "shulker_bullet",
            "small_fireball",
            "snowball",
            "evoker_fangs",
            "wither_skull",
            "tnt",
            "arrow",
            "egg",
            "cod",
            "salmon",
            "pufferfish",
            "tropical_fish",
            "bee",
            "ghast",
            "phantom",
            "lightning_bolt",
            "bat",
            "spectral_arrow",
            "trident",
            "potion",
            "elder_guardian",
            "squid",
        ]

        valid_entities = []
        for entity in ENTITY_LIST:
            if entity.replace("minecraft:", "") not in filter:
                valid_entities.append(entity)

        random_entity = randint(0, len(valid_entities) - 1)
        chosen_entity = valid_entities[random_entity]

        mc.post(f'summon {chosen_entity} {random_coords} {{Tags:["to_kill"]}}')

        chosen_entity = chosen_entity.replace("minecraft:", "")
        chosen_entity = chosen_entity.replace("_", " ")
        instructions["variable_name"] = chosen_entity

        return instructions

    elif action == "check":
        cmd_feedback = mc.post("execute if entity @e[tag=to_kill]")

        if "Test failed" in cmd_feedback:
            return True
        else:
            return False

    elif action == "play":
        words = instructions["message"].split(" ")

        random_cell = get_random_cell_on_board()

        filter = []
        for index, word in enumerate(words):
            word = word.lower()

            if word in filter:
                continue

            if f"minecraft:{word}" in ENTITY_LIST and word not in ENTITY_ACTION_FILTER:
                mc.post(f"summon {word} {random_cell}")

            elif f"minecraft:{word}" in BLOCK_LIST:
                random_cell.y += 15 + index
                cmd = f'summon minecraft:falling_block {random_cell} {{BlockState:{{Name:"minecraft:{word}"}},Time:1}}'
                mc.post(cmd)
                random_cell.y -= 15 + index

            if index == 2:
                break


def task_put_out_fire(action: str, instructions: dict = None) -> Union[dict, bool]:

    if action == "run":

        instructions = {"block_check": []}

        random_coords = get_random_cell_on_board()
        mc.set_block(random_coords, mc.Block("fire"))

        instructions["block_check"].append(random_coords)

        while randint(0, 3):
            random_coords = get_random_cell_on_board()
            mc.set_block(random_coords, mc.Block("fire"))

            instructions["block_check"].append(random_coords)

        return instructions

    elif action == "check":

        any_fire_remaining = True

        for coords in instructions["block_check"]:
            ret = mc.post(f"execute if block {coords} fire")

            any_fire_remaining = False
            if "Test passed" in ret:
                mc.set_block(coords, mc.Block("fire"))
                any_fire_remaining = True

        if any_fire_remaining:
            return False
        else:
            return True

    elif action == "play":
        words = instructions["message"].split(" ")

        random_cell = get_random_cell_on_board()

        filter = ["fire"]
        for index, word in enumerate(words):
            word = word.lower()

            if word in filter:
                continue

            if f"minecraft:{word}" in ENTITY_LIST and word not in ENTITY_ACTION_FILTER:
                mc.post(f"summon {word} {random_cell}")

            elif f"minecraft:{word}" in BLOCK_LIST:
                random_cell.y += 15 + index
                cmd = f'summon minecraft:falling_block {random_cell} {{BlockState:{{Name:"minecraft:{word}"}},Time:1}}'
                mc.post(cmd)
                random_cell.y -= 15 + index

            if index == 2:
                break


def task_blow_up_tnt(action: str, instructions: dict = None) -> Union[dict, bool]:

    if action == "run":

        instructions = {"block_check": []}

        random_coords = get_random_cell_on_board()
        mc.set_block(random_coords, mc.Block("tnt"))

        instructions["block_check"].append(random_coords)

        while randint(0, 3):
            random_coords = get_random_cell_on_board()
            mc.set_block(random_coords, mc.Block("tnt"))

            instructions["block_check"].append(random_coords)

        return instructions

    elif action == "check":
        any_tnt_remaining = True

        for coords in instructions["block_check"]:
            ret = mc.post(f"execute if block {coords} tnt")

            any_tnt_remaining = False
            if "Test passed" in ret:
                any_tnt_remaining = True

        if any_tnt_remaining:
            return False
        else:
            return True

    elif action == "play":
        words = instructions["message"].split(" ")

        random_cell = get_random_cell_on_board()

        filter = []
        for index, word in enumerate(words):
            word = word.lower()

            if word in filter:
                continue

            if f"minecraft:{word}" in ENTITY_LIST and word not in ENTITY_ACTION_FILTER:
                mc.post(f"summon {word} {random_cell}")

            elif f"minecraft:{word}" in BLOCK_LIST:
                random_cell.y += 15 + index
                cmd = f'summon minecraft:falling_block {random_cell} {{BlockState:{{Name:"minecraft:{word}"}},Time:1}}'
                mc.post(cmd)
                random_cell.y -= 15 + index

            if index == 2:
                break


def task_reach_the_goal(action: str, instructions: dict = None) -> Union[dict, bool]:

    if action == "run":

        instructions = {}

        random_coords = get_random_cell_on_board()

        filter = [
            "fireball",
            "dragon_fireball",
            "shulker_bullet",
            "small_fireball",
            "snowball",
            "evoker_fangs",
            "wither_skull",
            "tnt",
            "arrow",
            "egg",
            "cod",
            "salmon",
            "pufferfish",
            "tropical_fish",
            "bee",
            "ghast",
            "phantom",
            "lightning_bolt",
            "bat",
            "spectral_arrow",
            "trident",
            "potion",
            "elder_guardian",
            "dolphin",
        ]

        valid_entities = []
        for entity in ENTITY_LIST:
            if entity.replace("minecraft:", "") not in filter:
                valid_entities.append(entity)

        random_entity = randint(0, len(valid_entities) - 1)
        chosen_entity = valid_entities[random_entity]

        mc.post(f'summon {chosen_entity} {random_coords} {{Tags:["target"], NoAI:1b}}')

        chosen_entity = chosen_entity.replace("minecraft:", "")
        chosen_entity = chosen_entity.replace("_", " ")
        instructions["variable_name"] = chosen_entity

        random_coords = get_random_cell_on_board()
        instructions["goal_coords"] = random_coords
        mc.set_block(random_coords, mc.Block("stone_pressure_plate"))

        return instructions

    elif action == "check":

        coords = get_entity_pos(instructions["variable_name"].replace(" ", "_"))

        if str(coords) == str(instructions["goal_coords"]):
            return True
        else:
            return False

    elif action == "play":
        words = instructions["message"].split(" ")

        filter = ["left", "right", "up", "down"]
        entity = instructions["variable_name"].replace(" ", "_")
        for index, word in enumerate(words):
            word = word.lower()

            if word not in filter:
                continue

            if word == "left":
                ret = mc.post(f"execute as @e[type={entity}] at @s run tp @s ~-1 ~ ~")
                print(ret)

            elif word == "right":
                mc.post(f"execute as @e[type={entity}] at @s run tp @s ~1 ~ ~")

            elif word == "up":
                mc.post(f"execute as @e[type={entity}] at @s run tp @s ~ ~ ~-1")

            elif word == "down":
                mc.post(f"execute as @e[type={entity}] at @s run tp @s ~ ~ ~1")

            if index == 0:
                break


TASKS = [
    {"name": "Kill the {entity}", "function": task_kill_the_entity},
    {"name": "Put out the fire", "function": task_put_out_fire},
    {"name": "Blow up the TNT", "function": task_blow_up_tnt},
    {"name": "Bring {entity} to the goal", "function": task_reach_the_goal},
]

"""
    {"name": "Destroy the {structure}", "function": foo_task},
    {"name": "Push the {entity} in the void", "function": foo_task},
    {"name": "Turn on the {redstone_component}", "function": foo_task},
    {"name": "Craft the {item}", "function": foo_task},
    {"name": "Find the {ore}", "function": foo_task},
    {"name": "Battle royale!", "function": foo_task},""",


def play_task(task: dict):
    for element in TASKS:
        if element["name"] == task["name"]:
            return element["function"]("play", task["instructions"])


def check_task(task: dict) -> bool:
    for element in TASKS:
        if element["name"] == task["name"]:
            return element["function"]("check", task["instructions"])


def new_task(task: dict) -> dict:
    """
    When calling the function of a task, there is two possible "action" to call-out for:
        - run
        - check

    'run' starts the task whereas 'check' tests out the state of the task to determine if it was
    solved
    """
    task_dict = {}

    task_dict["instructions"] = task["function"]("run")

    task_dict["name"] = task["name"]

    if "variable_name" in task_dict["instructions"].keys():
        task_goal = re.sub(
            "({.*})", task_dict["instructions"]["variable_name"], task_dict["name"]
        )
    else:
        task_goal = task_dict["name"]

    print(f"Current task: {task_goal}")

    instructions = mc._set_text(
        task_goal,
        mc.BlockCoordinates(0, 0, 0),
        ["quartz"],
        "mixed",
        "east",
        mc.BlockHandler("replace"),
        0,
        mc.Block("air"),
    )
    zone = instructions["zone"]
    x_offset = (zone.pos2.x - zone.pos1.x) / 2

    player_pos = get_gamemaster_pos()
    player_pos.z -= TASK_TEXT_DISTANCE_SHIFT
    player_pos.y -= TASK_TEXT_DEPTH_SHIFT
    player_pos.x -= x_offset

    task_dict["text_zone"] = mc.set_text(
        task_goal,
        player_pos,
        style="mixed",
        palette=TASK_GOAL_PALETTE,
    )

    return task_dict


def clean_board():

    player_pos = get_gamemaster_pos()

    board_pos1 = copy(player_pos)

    board_pos1.x -= BOARD_SIZE / 2
    board_pos1.y -= BOARD_DEPTH_SHIFT - 1
    board_pos1.z -= BOARD_DISTANCE_SHIFT

    board_pos2 = copy(board_pos1)

    board_pos2.x += BOARD_SIZE - 1
    board_pos2.y += 40
    board_pos2.z -= BOARD_SIZE - 1

    zone = mc.Zone(board_pos1, board_pos2)
    zone.pos1.z += 2
    zone.pos2.z -= 2
    zone.pos1.x -= 2
    zone.pos2.x += 2

    for value in range(0, 256):
        zone.pos1.y = value
        zone.pos2.y = value

        block = mc.Block("air")
        mc.set_zone(zone, block, mc.BlockHandler("replace"))

    mc.post("execute as @e[type=!player] at @s run tp @s ~ 0 ~")
    mc.post("kill @e[type=!player]")

    text_pos1 = mc.BlockCoordinates(
        player_pos.x - 80,
        player_pos.y - TASK_TEXT_DEPTH_SHIFT,
        -TASK_TEXT_DISTANCE_SHIFT,
    )
    text_pos2 = mc.BlockCoordinates(
        player_pos.x + 80,
        player_pos.y - TASK_TEXT_DEPTH_SHIFT + 6,
        -TASK_TEXT_DISTANCE_SHIFT,
    )
    zone = mc.Zone(text_pos1, text_pos2)
    mc.set_zone(zone, mc.Block("air"))


def announce(text, palette: list = ["quartz"], scale: int = 0) -> mc.Zone:
    instructions = mc._set_text(
        text,
        mc.BlockCoordinates(0, 0, 0),
        palette,
        "mixed",
        "east",
        mc.BlockHandler("replace"),
        scale,
        mc.Block("air"),
    )
    zone = instructions["zone"]
    x_offset = (zone.pos2.x - zone.pos1.x) / 2

    player_pos = get_gamemaster_pos()
    player_pos.z -= TASK_TEXT_DISTANCE_SHIFT
    player_pos.y -= TASK_TEXT_DEPTH_SHIFT
    player_pos.x -= x_offset

    zone = mc.set_text(text, player_pos, style="mixed", palette=palette, scale=scale)

    return zone


# Could this function possibly not re-set every past lamp and only the current one?
# As in: instead of for-looping over the 1st, 2nd, 3rd lamp (etc.) it sets the 3rd directly
# To consider: it could skip a lamp depending on the time elapsed since the last function call
def clock(time: int = 0, option: str = None) -> str:

    if time > ROUND_TIME_SEC + 1:
        return "elapsed"

    clock_mechanism_pos = get_gamemaster_pos()

    clock_mechanism_pos.x -= BOARD_SIZE / 2
    clock_mechanism_pos.y -= 7
    clock_mechanism_pos.z += 7

    block = mc.Block("redstone_block")

    if option == "reset":
        clock_mechanism_pos.y += 2

        for _ in range(BOARD_SIZE):
            mc.set_block(clock_mechanism_pos, mc.Block("air"))
            clock_mechanism_pos.x += 1

        clock_mechanism_pos.y -= 3
        clock_mechanism_pos.x -= BOARD_SIZE + 1
        print(clock_mechanism_pos)
        ret = mc.set_block(clock_mechanism_pos, mc.Block("redstone_torch"))
        print(ret)
        sleep(0.1)
        ret = mc.set_block(clock_mechanism_pos, mc.Block("air"))
        print(ret)

    else:
        amount_of_lamp = int(time / (ROUND_TIME_SEC / BOARD_SIZE))
        clock_mechanism_pos.y += 2

        for _ in range(amount_of_lamp):
            mc.set_block(clock_mechanism_pos, mc.Block("redstone_wire"))
            clock_mechanism_pos.x += 1


def game_loop():

    now = time()

    task = {}
    task["text_zone"] = mc.Zone((0, 0, 0), (0, 0, 0))

    first_loop = True
    time_elapsed = False
    task_success = False

    task_index = 0

    shuffle(TASKS)

    while True:

        if not first_loop:

            if clock(time=time() - now) == "elapsed":
                time_elapsed = True

            elif check_task(task):
                task_success = True

        if first_loop or time_elapsed or task_success:

            mc.set_zone(task["text_zone"], mc.Block("air"))

            if task_success:
                zone = announce(TASK_SUCCESS_TEXT, TASK_SUCCESS_PALETTE, scale=0)
                sleep(TASK_OVER_WAIT_TIME_SEC)
                mc.set_zone(zone, mc.Block("air"))

            elif time_elapsed:
                zone = announce(TASK_FAILED_TEXT, TASK_FAILED_PALETTE)
                sleep(TASK_OVER_WAIT_TIME_SEC)
                mc.set_zone(zone, mc.Block("air"))

            clean_board()
            clock(option="reset")
            now = time()

            task = new_task(TASKS[task_index])

            if task_index >= len(TASKS) - 1:
                task_index = 0
                print("Shuffling the list of tasks:")
                shuffle(TASKS)
                task_name_list = [task["name"] for task in TASKS]
                print(f"New order: {task_name_list}")
            else:
                task_index += 1

            first_loop = False
            time_elapsed = False
            task_success = False

        chat = pytchat.create(video_id=CHAT_ID)
        for c in chat.get().sync_items():
            task["instructions"]["message"] = c.message
            play_task(task)

        sleep(0.1)


def prepare_board():

    player_pos = get_gamemaster_pos()

    ####################
    # -- Main board -- #
    ####################

    board_pos1 = copy(player_pos)

    board_pos1.x -= BOARD_SIZE / 2
    board_pos1.y -= BOARD_DEPTH_SHIFT
    board_pos1.z -= BOARD_DISTANCE_SHIFT

    board_pos2 = copy(board_pos1)

    board_pos2.x += BOARD_SIZE - 1
    board_pos2.z -= BOARD_SIZE - 1

    # Calculate the zone
    zone = mc.Zone(board_pos1, board_pos2)
    block = BOARD_TEXTURE
    cmd = mc._set_zone(zone, block, mc.BlockHandler("replace"))

    # Create the command block that will make it self-repair
    command_block = mc.Block("repeating_command_block")
    nbt = mc.NBT({"Command": cmd})
    command_block.nbt = nbt

    # Place it under the player
    coords = mc.BlockCoordinates(player_pos.x, player_pos.y - 2, player_pos.z)
    mc.set_block(coords, command_block)

    # Trigger the self-repair
    coords.y -= 1
    block = mc.Block("redstone_block")
    mc.set_block(coords, block)

    ###############
    # -- Clock -- #
    ###############

    clock_pos = copy(board_pos1)
    clock_pos.y -= 1

    clock_block = mc.Block("redstone_lamp")
    block_handler = mc.BlockHandler("replace")

    support_block = mc.Block("bedrock")
    activator_block = mc.Block("redstone_torch")

    # Bottom part
    support_coords = mc.BlockCoordinates(clock_pos.x - 1, clock_pos.y, clock_pos.z + 12)
    activator_coords = mc.BlockCoordinates(
        clock_pos.x - 1, clock_pos.y + 1, clock_pos.z + 12
    )

    mc.set_block(support_coords, support_block)
    mc.set_block(activator_coords, activator_block)

    # Upper part
    support_coords = mc.BlockCoordinates(
        clock_pos.x - 1, clock_pos.y + 3, clock_pos.z + 12
    )
    activator_coords = mc.BlockCoordinates(
        clock_pos.x - 1, clock_pos.y + 4, clock_pos.z + 12
    )

    mc.set_block(support_coords, support_block)
    mc.set_block(activator_coords, activator_block)

    # This loop will do an action for each "tick" (as a block) of the clock
    for _ in range(0, BOARD_SIZE):

        # Place clock block
        mc.set_block(clock_pos, clock_block)

        # Creates self-repair for "off" state
        clock_block.blockstate.lit = False
        cmd = mc._set_block(clock_pos, clock_block, block_handler)

        command_block_off = mc.Block("repeating_command_block")
        nbt = mc.NBT({"Command": cmd})
        command_block_off.nbt = nbt

        # Creates self-repair for "on" state
        clock_block.blockstate.lit = True
        cmd = mc._set_block(clock_pos, clock_block, block_handler)

        command_block_on = mc.Block("repeating_command_block")
        nbt = mc.NBT({"Command": cmd})
        command_block_on.nbt = nbt

        # Place the mechanism relative to the clock "tick"
        coords = mc.BlockCoordinates(clock_pos.x, clock_pos.y, clock_pos.z + 10)
        mc.set_block(coords, command_block_off)

        coords.y += 3
        mc.set_block(coords, command_block_on)

        coords.y -= 2
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z += 1
        coords.y -= 1
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z += 1
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z -= 1
        coords.y += 1
        block = mc.Block("repeater")
        block.blockstate.facing = "south"
        mc.set_block(coords, block)

        coords.z += 1
        block = mc.Block("redstone_wire")
        mc.set_block(coords, block)

        coords.z -= 2
        coords.y += 3
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z += 1
        coords.y -= 1
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z += 1
        block = mc.Block("bedrock")
        mc.set_block(coords, block)

        coords.z -= 1
        coords.y += 1
        block = mc.Block("repeater")
        block.blockstate.facing = "south"
        mc.set_block(coords, block)

        # Go to the next clock "tick"
        clock_pos.x += 1


def prepare_gamemaster():

    coords = mc.BlockCoordinates(0.5, GAMEMASTER_HEIGHT, 0.5)

    # Once online, set a block in the sky for the gamemaster to stand on
    mc.set_block(coords, mc.Block("bedrock"))

    # Then tp the gamemaster on the block
    coords.y += 1
    mc.post(f"tp {GAMEMASTER} {coords} {GAMEMASTER_YAW} {GAMEMASTER_PITCH}")

    print(f"Gamemaster: '{GAMEMASTER}' has been positionned")


def clean_terrain():

    # Clean up the zone in which the game plays out
    for value in range(256):
        pos1 = mc.BlockCoordinates(90, value, 90)
        pos2 = mc.BlockCoordinates(-90, value, -90)
        clean_up_zone = mc.Zone(pos1, pos2)
        mc.set_zone(clean_up_zone, mc.Block("air"))


def wait_gamemaster():

    prompted = False
    prompt = f"The gamemaster: '{GAMEMASTER}' must connect to the server in order for the game to start."

    # Test that the Gamemaster is connected to the server
    while "Test failed" in mc.post(f"execute if entity {GAMEMASTER}"):
        if not prompted:
            print(prompt)
            prompted = True
        sleep(2)

    if prompted:
        print(f"Gamemaster: '{GAMEMASTER}' connected")


def init_server():
    list_of_cmd = [
        f"whitelist on",
        f"time set noon",
        f"gamerule sendCommandFeedback false",
        f"gamerule fireDamage false",
    ]

    print("Initializing the server by running the initial following commands:")
    print("=====================================")
    for cmd in list_of_cmd:

        print(f"Running: '/{cmd}'")

        cmd_feedback = mc.post(cmd)
        print(f"Feedback: {cmd_feedback}")

        print("=====================================")
    print("Done with initialization\n")


if __name__ == "__main__":

    try:
        mc.connect("localhost", "test")
    except ConnectionRefusedError:
        mc.create()
        mc.connect("localhost", "test")

    if INITIALIZE_SERVER:
        init_server()

    wait_gamemaster()

    if CLEAN_TERRAIN:
        clean_terrain()

    if PREPARE_GAMEMASTER:
        prepare_gamemaster()

    if PREPARE_BOARD:
        prepare_board()

    seed(int(time()))

    if GAME_LOOP:
        game_loop()
