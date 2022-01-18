import time


def render_game_over(window, game):
    

    game_over_mgs = "GAME OVER"
    window_height, window_width = window.getmaxyx()

    while game.state == "game_over":
        window.addstr(
            window_height // 2,
            window_width // 2 - len(game_over_mgs) // 2,
            game_over_mgs
        )
        window.refresh()
        time.sleep(0.3)
