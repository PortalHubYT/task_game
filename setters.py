from env import *
from fetchers import get_gamemaster_pos


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
