

def render_entity(game, window):

    window.erase()
    py, px = game.pointer_pos
    map_array = game.game_map["map_array"]
    entities = game.pool.entities

    ent_ids = map_array[py][px]
    line = 1
    sy, sx = window.getmaxyx()
    for ent_id in ent_ids:
        ent = entities[ent_id]
        window.addstr(line, 1, f"entity_id: {ent_id}")
        line += 1
        for k, v in ent.items():
            key = str(k)
            value = str(v)
            if len(value) > sx - 10 :
                value = value[:sx - 10] + "..."
            l = f"{key}: {value}"
            window.addstr(line, 1, l)
            line += 1
            if line > sy - 2:
                break
            line += 1
        window.addstr(line, 1, (sx - 2) * "-")
        line += 1
    window.refresh()
    loop = True
    while loop:
        key = window.getch()
        for char in game.config["keyboard"]["debug_show_entity_info"]:
            if key == ord(char):
                loop = False
