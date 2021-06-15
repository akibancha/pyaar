
def render(map_window,
           game):
    win_y, win_x = map_window.getmaxyx()
    line = 1
    for elem in game.log[::-1]:
        map_window.addstr(line, 1, elem)
        line += 1
        if line == win_y - 1:
            break
    map_window.refresh()

