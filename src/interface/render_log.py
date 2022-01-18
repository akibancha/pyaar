
def render(map_window,
           game):
    win_y, win_x = map_window.getmaxyx()
    line = 2
    for elem in game.log[::-1]:
        map_window.addstr(win_y - line, 1, elem)
        line += 1
        if win_y - line < 1:
            break
        
    map_window.refresh()

