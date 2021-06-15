import curses
import random

import game_map
import game

import systems.move
import systems.fov
import systems.perform
import systems.simple_ai


def main(screen):

    screen.idcok(False)
    screen.idlok(False)

    curses.curs_set(False)

    test = game.Game()
    test.init_blueprints()
    test.init_game_map(50, 50)

    player_b = {"name": "player", "char": [["@", "white", "green"]],
                "movement_cost": 15,
                "unpassable": True,
                "update_fov": True,
                "FOV": {"range": 10, "can_see": set()}}

    test.init_player(player_b)

    game_map.create_map(game=test, level=1)

    pad = curses.newwin(24, 80, 1, 1)

    test.load_config("config.json")

    player_pos = (test.
                  pool.
                  entities[random.choice(test.game_map["rooms"])]["center"])
    test.place_entity(pos=player_pos,
                      entity_id=test.player_id, add_pos_comp=True)
    test.pointer_pos = player_pos

    test.pool.add_system(system=systems.move.MoveSystem, name="move", layer=2)
    test.pool.add_system(system=systems.fov.Fov, name="fov", layer=3)
    test.pool.add_system(system=systems.perform.Perform, name="perform", layer=0)
    test.pool.add_system(system=systems.simple_ai.Simple_Ai_System, name="simple_ai", layer=1)


    yy, xx = player_pos

    test.log.append("Welcome!")
    test.log.append("Use the vi keys or the numpad to move")
    pad.timeout(test.config["debug"]["keyboard_timeout"])
    test.pool.update(["fov"])
    while test.state != "exit":
        test.perform_render(screen)
        key = pad.getch()

        if key >= 0 and not test.player.get("Perform"):
            test.perform_input(chr(key))

        while test.player.get("Perform"):
            test.pool.update()
            test.round += 1


curses.wrapper(main)

print("Thank you for playing pyaar!")
print("Good Bye!")
