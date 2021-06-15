from typing import List, Iterator
from mytpyes import Vec2int


def get_neighbours_2d(array: List,
                      pos: Vec2int,
                      map_size: Vec2int = None,
                      include_self: bool = False,
                      diagonal_neighbours: bool = True) -> List[Vec2int]:

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

    return [(pos_y + step_y, pos_x + step_x)
            for step_y in steps
            for step_x in steps
            if (step_y, step_x) not in exclude
            and pos_y + step_y in map_y_range
            and pos_x + step_x in map_x_range]


def bresenham_line(start: Vec2int,
                   end: Vec2int) -> Iterator[Vec2int]:

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
