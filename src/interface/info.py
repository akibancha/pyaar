

def render_info_window(window, game):

    window_height, window_width = window.getmaxyx()

    name = game.player["name"]
    current_hp = game.player["health"]["current_hp"]
    max_hp = game.player["health"]["max_hp"]
    weapon = game.player["equipment"].get("weapon")
    armor = game.player["equipment"].get("armor")
    light_source = game.player["equipment"].get("light_source")
    if weapon:
        weapon = game.pool.entities[weapon]["name"]
    else:
        weapon = "none"
    if armor:
        armor = game.pool.entities[armor]["name"]
    else:
        armor = "none"
    if light_source:
        light_source = game.pool.entities[light_source]["name"]
    else:
        light_source = "none"



    line = 1
    infos = [
        "---[Stats]---",
        f"HP: {current_hp} / {max_hp}",
        "MP: not inplemented",
        f"Inventory slots: {len(game.player['inventory']['items'])} / {game.player['inventory']['slots']}",
        f"Movement cost: {game.player['movement_cost']}",
        "Action cost: not implemented",
        "---[Equipment]---",
        f"Weapon: {weapon}",
        f"Armor: {armor}",
        f"Light source: {light_source}",
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
