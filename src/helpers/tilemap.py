from typing import Any, List, Iterator, Tuple, Optional


def get_neighbours_2d(
    array: List[List[Any]],
    pos: Tuple[int, int],
    map_size: Optional[Tuple[int, int]] = None,
    include_self: bool = False,
    diagonal_neighbours: bool = True,
) -> List[Tuple[int, int]]:

    if not map_size:
        map_size_y = len(array)
        map_size_x = len(array[0])
    else:
        map_size_y, map_size_x = map_size

    pos_y, pos_x = pos

    map_y_range = range(map_size_y)
    map_x_range = range(map_size_x)

    steps = range(0)
    exclude = set()

    if diagonal_neighbours and not include_self:
        steps = range(-1, 2)
        exclude = {(0, 0)}

    if diagonal_neighbours and include_self:
        steps = range(-1, 2)

    if not diagonal_neighbours and not include_self:
        steps = range(-1, 2)
        exclude = {(0, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)}

    if not diagonal_neighbours and include_self:
        steps = range(-1, 2)
        exclude = {(1, 1), (-1, -1), (-1, 1), (1, -1)}

    return [
        (pos_y + step_y, pos_x + step_x)
        for step_y in steps
        for step_x in steps
        if (step_y, step_x) not in exclude
        and pos_y + step_y in map_y_range
        and pos_x + step_x in map_x_range
    ]


def bresenham_line(
    start: Tuple[int, int],
    end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:

    y_start, x_start = start
    y_end, x_end = end

    dx = abs(x_end - x_start)
    sx = 1 if x_start > x_end else -1
    dy = -abs(y_end - y_start)
    sy = 1 if y_start > y_end else -1
    err = dx + dy

    while True:
        if (y_start, x_start) == (y_end, y_start):
            break
        err2 = err * 2
        if err2 >= dy:
            err += dy
            x_start += sx
        if err2 <= dx:
            err += dx
            y_start += sy
        yield y_start, x_start


def check_pos_exist(
    game,
    pos: Tuple[int, int]
) -> bool:

    map_height = game.game_map["map_height"]
    map_width = game.game_map["map_width"]

    pos_y, pos_x = pos

    if pos_y in range(map_height) or pos_x in range(map_width):
        return True
    else:
        return False

