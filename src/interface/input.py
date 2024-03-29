from typing import Optional

import interface.debug
from helpers.movement import movement_vectors


def create_movement_component(direction: str, game):
    move_component = {"velo": movement_vectors[direction]}
    rounds = game.player["movement_cost"]
    perform_component = {"Perform": {"round": (0, rounds),
                         "components": move_component}}
    return perform_component


def handle_input(game,
                 key: str) -> Optional[str]:

    keys = game.config["keyboard"]

    if game.state == "normal":

        for k, v in keys.items():
            if "move_" in k and key in v:
                if game.pointer_bound:
                    component = create_movement_component(k.
                                                          replace("move_", ""),
                                                          game)
                    game.pool.add_components_to_entity(component,
                                                       game.player_id)
                    return None
                else:
                    py, px = game.pointer_pos
                    dpy, dpx = movement_vectors[k.replace("move_", "")]
                    npy, npx = py + dpy, px + dpx
                    if (npy in range(game.game_map["map_height"]) and
                       npx in range(game.game_map["map_width"])):
                        game.pointer_pos = (npy, npx)
                    return

            if "quit" in k and key in v:
                game.state = "exit"

            if "toggle_fov" in k and key in v:
                if game.config["debug"]["disable_fov"]:
                    game.config["debug"]["disable_fov"] = False
                    log = "<debug>: fov has been enabled"
                    game.log.append(log)
                    return
                game.config["debug"]["disable_fov"] = True
                log = "<debug>: fov has been disabled"
                game.log.append(log)
                return

            if "toggle_collision" in k and key in v:
                if game.config["debug"]["disable_collision"]:
                    game.config["debug"]["disable_collision"] = False
                    log = "<debug>: collision has been enabled"
                    game.log.append(log)
                    return
                game.config["debug"]["disable_collision"] = True
                log = "<debug>: collision has been disabled"
                game.log.append(log)
                return

            if "look" in k and key in v:
                if game.pointer_bound:
                    game.pointer_bound = False
                else:
                    game.pointer_bound = True

            if "change_fov_entity" in k and key in v:
                if not game.pointer_bound:
                    old_fov_entity = game.pointer_entity
                    y, x = game.pointer_pos
                    new_fov_entity = game.game_map["map_array"][y][x][-1]
                    if game.pool.entities[new_fov_entity].get("FOV"):
                        game.pointer_entity = new_fov_entity
                        log = f"<debug>: changed fov entity. {old_fov_entity} -> {game.pointer_entity}"
                        game.log.append(log)
                    else:
                        log = f"<debug>: entity {new_fov_entity} does not have a field of view"
                        game.log.append(log)

            if "debug_show_entity_info" in k and key in v:
                if not game.pointer_bound:
                    interface.debug.render_entity(game=game, window=game.base_windows["std"])
            if "debug_show_log" in k and key in v:
                if not game.pointer_bound:
                    interface.debug.render_log(game=game, window=game.base_windows["std"])

            if "inventory" in k and key in v:
                game.state = "inventory"
