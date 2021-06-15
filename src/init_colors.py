import curses


colors = {"black": curses.COLOR_BLACK,
          "white": curses.COLOR_WHITE,
          "red": curses.COLOR_RED,
          "blue": curses.COLOR_BLUE,
          "yellow": curses.COLOR_YELLOW,
          "green": curses.COLOR_GREEN,
          "magenta": curses.COLOR_MAGENTA,
          "cyan": curses.COLOR_CYAN}


def create_color_book() -> dict:
    color_book = dict()
    color_pair = 1
    for foreground_key, foreground_color in colors.items():
        color_book[foreground_key] = dict()
        for background_key, background_color in colors.items():
            color_book[foreground_key][background_key] = color_pair
            curses.init_pair(color_pair, foreground_color, background_color)
            color_pair += 1
    return color_book
