from interface.window import render_resize_msg

def render_entity(game, window) -> None:

    py: int
    px: int
    py, px = game.pointer_pos

    map_array: list[list[list[int]]]
    map_array = game.game_map["map_array"]

    entities: dict[int: dict[str: Any]]
    entities = game.pool.entities

    ent_ids: list[int]
    ent_ids = map_array[py][px]

    number_of_ents: int = len(ent_ids)

    str_format: dict[str: str]
    if number_of_ents > 1:
        str_format = {
                "verb": "are",
                "subject": "entities"
                }
    else:
        str_format = {
                "verb": "is",
                "subject": "entity"
                }

    top_pos: int = 0
    min_screen_size: Tuple[int, int]
    min_screen_size = (game.config["screen_size"]["height"], game.config["screen_size"]["width"])
    while True:
        render_resize_msg(screen=window, min_size=min_screen_size, frames=60)
        line: int = 1

        sy: int
        sx: int
        sy, sx = window.getmaxyx()

        str_list: list[str] = list()
        str_list.append(f"there {str_format['verb']} {len(ent_ids)} {str_format['subject']} on map pos {(py, px)}")
        str_list.append(":::")

        ent_id: int
        ent_nr: int = 1
        for ent_id in ent_ids:
            ent: dict[str: Any] = entities[ent_id]
            str_list.append(f"entity {ent_nr} with id: {ent_id}")
            ent_nr += 1
            str_list.append(f" => has currently {len(ent)} components:")
            str_list.append(" ↓")
            comp_nr: int = 1
            k: str
            v: Any
            for k, v in ent.items():
                key: str = str(k)
                value: str = str(v)
                l: str = f" | {comp_nr} :: {key}: {value}"
                if len(l) >= sx - 5:
                    l = l[:sx - 5] + "..."
                str_list.append(l)
                comp_nr += 1
            str_list.append("----")
        window.erase()
        line_nr: int
        line: str
        for line_nr, line in enumerate(str_list[top_pos:], start=1):
            if line_nr <= sy - 1:
                window.addstr(line_nr, 1, line)
        window.refresh()
        key: int = window.getch()
        for char in game.config["keyboard"]["debug_show_entity_info"]:
            if key == ord(char):
                break
        for char in game.config["keyboard"]["debug_show_entity_info_scroll_up"]:
            if key == ord(char):
                if not top_pos - 1 < 0:
                    top_pos += -1
        for char in game.config["keyboard"]["debug_show_entity_info_scroll_down"]:
            if key == ord(char):
                if not top_pos + 1 > len(str_list) and len(str_list) - top_pos > sy:
                    top_pos += 1

class DebugLog:

    def __init__(max_amount: int = 1000) -> None:
        self.max_amount: int = max_amount
        self.log_mgs_list: list[str] = list()

    def add_log(self, log_mgs: str) -> None:
        if len(self.log_mgs_list) >= self.max_amount:
            del self.log_mgs_list[0]
        self.log_mgs_list.append(log_mgs)
