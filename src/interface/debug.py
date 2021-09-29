

def render_entity(game, window):

    py, px = game.pointer_pos
    map_array = game.game_map["map_array"]
    entities = game.pool.entities

    ent_ids = map_array[py][px]
    line = 1
    sy, sx = window.getmaxyx()
    str_list = list()
    str_list.append(f"entities on map pos {(py, px)}")
    str_list.append(f"::::")
    for ent_id in ent_ids:
        ent = entities[ent_id]
        str_list.append(f"entity_id: {ent_id}")
        str_list.append(f"this entity currently has {len(ent)} components:")
        str_list.append("↓")
        comp_nr = 1
        for k, v in ent.items():
            key = str(k)
            value = str(v)
            if len(value) > sx - 10 :
                value = value[:sx - 10] + "..."
            l = f"{comp_nr}::{key}: {value}"
            str_list.append(l)
            comp_nr += 1
        str_list.append(f"----")
    top_pos = 0
    loop = True
    while loop:
        window.erase()
        for line_nr, line in enumerate(str_list[top_pos:], start=1):
            if line_nr <= sy - 1:
                window.addstr(line_nr, 1, line)
        window.refresh()
        key = window.getch()
        for char in game.config["keyboard"]["debug_show_entity_info"]:
            if key == ord(char):
                loop = False
        for char in game.config["keyboard"]["debug_show_entity_info_scroll_up"]:
            if key == ord(char):
                if not top_pos - 1 < 0:
                    top_pos += -1
        for char in game.config["keyboard"]["debug_show_entity_info_scroll_down"]:
            if key == ord(char):
                if not top_pos + 1 > len(str_list) and len(str_list) - top_pos > sy:
                    top_pos += 1


