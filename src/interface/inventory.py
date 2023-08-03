from string import ascii_letters
from interface.info import render_info_window


def draw_inventory(window, content) -> None:
    window.erase()
    window.box()
    window.addstr(0, 2, "[Inventory]-[Press Q to exit]")
    line = 2
    for item in content:
        _str = f"{item[0]} -> {item[2]}"
        window.addstr(line, 1, _str)
        line += 1
    window.refresh()


def draw_item_screen(window, content) -> None:
    window.erase()
    window.box()
    window.addstr(0, 2, f"[{content[0]}]-[Press Q to exit or B to return to the inventory]")
    line = 1
    window.addstr(line, 2, content[1])
    line +=2
    window.addstr(line, 2, content[2])
    window.refresh()


def item_screen_loop(game, window, item_id) -> None:
    while True:
        render_info_window(game=game, window=game.base_windows["info"])
        item = game.pool.entities[item_id] 
        desc = item.get("desc")
        if not desc:
            desc = ""
        inter = ["[d] drop"]
        if item.get("item") and item.get("weapon"):
            if game.player.get("equipment"):
                if game.player["equipment"]["weapon"] == item_id:
                    inter.append("[u] unequip")
                else:
                    inter.append("[e] equip")
        content = [item["name"], desc, " ".join(inter)]
        draw_item_screen(window, content)
        keypress = window.getch()

        match chr(keypress):
            case "B":
                break
            case "Q":
                game.state = "normal"
                break
            case "e":
                game.equip_item(game.player_id, item_id)
            case "u":
                if item.get("weapon"):
                    game.player["equipment"]["weapon"] = None


def iventory_loop(game, window) -> None:
    if not game.player_id or not game.pool.entities[game.player_id].get("inventory"):
        game.state = "normal"
        return
    inventory = game.pool.entities[game.player_id].get("inventory")
    if inventory:
        items = [(ascii_letters[idx], id, game.pool.entities[id]["name"]) for idx, id in enumerate(inventory["items"])] 
        draw_inventory(window, items)

        keypress = window.getch()
        if chr(keypress) == "Q":
            game.state = "normal"
            return
        if ascii_letters.index(chr(keypress)) <= len(items) and chr(keypress) in ascii_letters:
            item_screen_loop(game, window, items[ascii_letters.index(chr(keypress))][1])




