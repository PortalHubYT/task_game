from env import *
from fetchers import get_gamemaster_pos


def clean_terrain():

    # Clean up the zone in which the game plays out
    for value in range(256):
        pos1 = mc.BlockCoordinates(90, value, 90)
        pos2 = mc.BlockCoordinates(-90, value, -90)
        clean_up_zone = mc.Zone(pos1, pos2)
        mc.set_zone(clean_up_zone, mc.Block("air"))


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

