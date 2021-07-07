from env import *


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
