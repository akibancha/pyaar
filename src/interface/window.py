import time
import curses
from typing import Optional

from mytpyes import Vec2int
import helpers.math


def test_min_screen_size(min_size: Vec2int, screen) -> bool:

    screen_size_y, screen_size_x = screen.getmaxyx()
    min_y, min_x = min_size

    return screen_size_y >= min_y and screen_size_x >= min_x


def render_resize_msg(min_size: Vec2int, screen, frames: int):

    screen_size_y, screen_size_x = screen.getmaxyx()
    min_y, min_x = min_size

    while not test_min_screen_size((min_y, min_x), screen):
        screen.erase()

        screen_size_y, screen_size_x = screen.getmaxyx()

        if screen_size_y < min_y:
            resize_info_y = f"{abs(screen_size_y - min_y)} chars to small"
        else:
            resize_info_y = "|great|"
        if screen_size_x < min_x:
            resize_info_x = f"{abs(screen_size_x - min_x)} chars to small"
        else:
            resize_info_x = "|great|"

        text_line_1 = (f"The minimal terminal size is set to y:{min_y}, " +
                       f"x:{min_x}")
        text_line_2 = (f"Your current terminal is y:{screen_size_y}, " +
                       f"x:{screen_size_x}")
        text_line_3 = "Resize your terminal, please."
        text_line_4 = f"y:{resize_info_y} x:{resize_info_x}"

        y = screen_size_y // 2
        for line in [text_line_1, text_line_2, text_line_3, text_line_4]:
            x = screen_size_x // 2 - len(line) // 2
            try:
                screen.addstr(y, x, line)
            except curses.error:
                pass
            y += 1

        time.sleep(1 / frames)
        screen.refresh()


def set_base_windows(game, screen, refresh: Optional[bool] = False):

    screen_size_y, screen_size_x = screen.getmaxyx()

    (config_map_window_size_y,
     config_map_window_size_x) = (game.config["base_window_sizes"]
                                             ["map_window"])
    (config_log_window_size_y,
     config_log_window_size_x) = (game.config["base_window_sizes"]
                                             ["log_window"])
    (config_info_window_size_y,
     config_info_window_size_x) = (game.config["base_window_sizes"]
                                              ["info_window"])

    map_window_size_y = int(helpers.
                            math.
                            percentage_value(config_map_window_size_y,
                                             screen_size_y))
    map_window_size_x = int(helpers.
                            math.
                            percentage_value(config_map_window_size_x,
                                             screen_size_x))

    log_window_size_y = int(helpers.
                            math.
                            percentage_value(config_log_window_size_y,
                                             screen_size_y))
    log_window_size_x = int(helpers.
                            math.
                            percentage_value(config_log_window_size_x,
                                             screen_size_x))

    info_window_size_y = int(helpers.
                             math.
                             percentage_value(config_info_window_size_y,
                                              screen_size_y))
    info_window_size_x = int(helpers.
                             math.
                             percentage_value(config_info_window_size_x,
                                              screen_size_x))

    map_window = curses.newwin(map_window_size_y,
                               map_window_size_x,
                               0,
                               0)
    log_window = curses.newwin(log_window_size_y,
                               log_window_size_x,
                               map_window_size_y,
                               0)
    info_window = curses.newwin(info_window_size_y,
                                info_window_size_x,
                                0,
                                map_window_size_x)

    game.base_windows["map"] = map_window
    game.base_windows["log"] = log_window
    game.base_windows["info"] = info_window

    if refresh:
        for x in [map_window, log_window, info_window]:
            x.box()
            x.refresh()
