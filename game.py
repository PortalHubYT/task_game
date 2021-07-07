from env import *
from fetchers import get_gamemaster_pos
from setters import prepare_board, prepare_gamemaster, init_server
from utils import announce, wait_gamemaster, clean_terrain, clean_board
from tasks import TASKS

# TODO: Add a barrier wall in front of the player
# TODO: Read and store message in async, yield them to the gameloop and clean up the queue each tasks #funyrom?
# TODO: Find a final and durable solution for the command blocks in-game


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
