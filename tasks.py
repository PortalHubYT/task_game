from env import *
from fetchers import get_random_cell_on_board, get_entity_pos


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


def foo_task():
    print("This task is not implemented yet")


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
