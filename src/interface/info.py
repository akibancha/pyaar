

def render_info_window(window, game):

    window_height, window_width = window.getmaxyx()

    name = game.player["name"]
    current_hp = game.player["health"]["current_hp"]
    max_hp = game.player["health"]["max_hp"]

    line = 1
    infos = [
        "---[Stats]---",
        f"HP: {current_hp}/{max_hp}",
        "MP: not inplemented",
        "Inventory slots: not implemented",
        f"Movement cost: {game.player['movement_cost']}",
        "Action cost: not implemented",
        "---[Equipment]---",
        "Armor: not implemented",
        "Weapon: not implemented",
        "Torch: not implemented",
        "---[Status]---",
        "not implemented"
    ]
    window.addstr(
        0,
        2,
        f"[{name}]"
    )

    for info in infos:
        window.addstr(line, 2, info)
        line += 1

    window.refresh()
