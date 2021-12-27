import curses
import random
from typing import Tuple, Set


def get_draw_range(
        pointer_pos: Tuple[int, int],
        map_size: Tuple[int, int],
        window_size: Tuple[int, int],
        buffer: int
    ) -> Tuple[range, range]:

    # set pointer pos
    pointer_y, pointer_x = pointer_pos

    # set window size
    win_height, win_width = window_size
    win_height += -buffer * 2
    win_width += -buffer * 2

    # set map size
    map_height, map_width = map_size

    # correct draw sizes in case of a very small map
    if win_height > map_height:
        win_height = map_height
    if win_width > map_width:
        win_width = map_width

    # set the y range begin and end
    draw_y_begin = pointer_y - win_height // 2
    draw_y_end = pointer_y + win_height // 2
    # correct for an odd numbered window size
    if win_height % 2 != 0:
        draw_y_end += 1

    # correct draw ranges
    if draw_y_begin < 0:
        draw_y_begin = 0
        draw_y_end = win_height
    if draw_y_end > map_height:
        draw_y_begin = map_height - win_height
        draw_y_end = map_height

    # do the same with the x range
    # vvv
    draw_x_begin = pointer_x - win_width // 2
    draw_x_end = pointer_x + win_width // 2
    # correct for an odd numbered window size
    if win_width % 2 != 0:
        draw_x_end += 1

    # correct draw ranges
    if draw_x_begin < 0:
        draw_x_begin = 0
        draw_x_end = win_width
    if draw_x_end > map_width:
        draw_x_begin = map_width - win_width
        draw_x_end = map_width

    return range(draw_y_begin, draw_y_end), range(draw_x_begin, draw_x_end)


def render(game,
           map_window,
           fov: bool,
           fov_entity: int = None,
           pointer_pos: Tuple[int, int] = (0, 0)) -> None:

    map_window.box()

    window_size_y, window_size_x = map_window.getmaxyx()

    game_map = game.game_map
    game_tile_map = game_map["map_array"]
    game_map_height = game_map["map_height"]
    game_map_width = game_map["map_width"]
    buffer = 3
    draw_y, draw_x = get_draw_range(pointer_pos=pointer_pos,
                                    map_size=(game_map_height, game_map_width),
                                    window_size=(window_size_y, window_size_x),
                                    buffer=buffer)

    debug_string = f"({draw_y}, {draw_x}, {game.round}, {game.pointer_pos})"
    map_window.addstr(0, 1, debug_string)
    fov_set: Set[Tuple[int, int]] = set()
    if fov:
        fov_set = game.pool.entities[fov_entity]["FOV"]
    for window_y, map_y in enumerate(draw_y, buffer):
        for window_x, map_x in enumerate(draw_x, buffer):
            ent_id = game_tile_map[map_y][map_x][-1]
            ent = game.pool.entities[ent_id]
            char = ent.get("char")
            char_list = random.choice(char)
            char, fg, bg = char_list
            color = game.colors[fg][bg]
            if (fov
               and (map_y, map_x) not in fov_set
               and not game.config["debug"]["disable_fov"]):
                char = None
            if char:
                map_window.addstr(window_y, window_x,
                                  char, curses.color_pair(color))
            if not game.pointer_bound:
                py, px = pointer_pos
                if map_y == py and map_x == px:
                    map_window.addstr(window_y, window_x, "X")
    map_window.refresh()
