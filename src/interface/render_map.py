import curses
import random
from typing import Tuple, Set

from mytpyes import Vec2int


def get_draw_range(pointer: Vec2int,
                   map: Vec2int,
                   window: Vec2int) -> Tuple[range, range]:

    pointer_y, pointer_x = pointer

    win_size_y, win_size_x = window

    map_size_y, map_size_x = map

    draw_y_begin = pointer_y - win_size_y // 2
    draw_y_end = pointer_y + win_size_y // 2

    draw_x_begin = pointer_x - win_size_x // 2
    draw_x_end = pointer_x + win_size_x // 2

    if pointer_y >= map_size_y - win_size_y // 2:
        fix_value = pointer_y - map_size_y
        draw_y_begin += -fix_value - win_size_y // 2
        draw_y_end = map_size_y

    if pointer_x >= map_size_x - win_size_x // 2:
        fix_value = pointer_x - map_size_y
        draw_x_begin += -fix_value - win_size_x // 2
        draw_x_end = map_size_x

    if draw_y_begin <= 0:
        draw_y_begin = 0
        if win_size_y < map_size_y:
            draw_y_end = win_size_y
        else:
            draw_y_end = map_size_y

    if draw_x_begin <= 0:
        draw_x_begin = 0
        if win_size_x < map_size_x:
            draw_x_end = win_size_x
        else:
            draw_x_end = map_size_x

    return (range(draw_y_begin, draw_y_end - 2),
            range(draw_x_begin, draw_x_end - 2))


def render(game,
           map_window,
           fov: bool,
           fov_entity: int = None,
           pointer_pos: Vec2int = (0, 0)) -> None:

    map_window.box()

    window_size_y, window_size_x = map_window.getmaxyx()

    game_map = game.game_map
    game_tile_map = game_map["map_array"]
    game_map_height = game_map["map_height"]
    game_map_width = game_map["map_width"]
    draw_y, draw_x = get_draw_range(pointer_pos,
                                    (game_map_height, game_map_width),
                                    (window_size_y, window_size_x))

    map_window.addstr(0, 1, f"({draw_y}, {draw_x}, {game.round})")
    fov_set: Set[Vec2int] = set()
    if fov:
        fov_set = game.pool.entities[fov_entity]["FOV"]
    for window_y, map_y in enumerate(draw_y, 1):
        for window_x, map_x in enumerate(draw_x, 1):
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
