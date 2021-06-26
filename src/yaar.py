import curses
import random

import game_map
import game

import systems.move
import systems.fov
import systems.perform
import systems.simple_ai


def main(screen) -> None:
    """
    The main function of this game.
    It Initializes the main components of the game and starts the game loop.

    :return None

    """

    # deactivate hardware character/line editing
    # TODO make this part of the config
    screen.idcok(False)
    screen.idlok(False)

    # deactivate terminal cursor
    curses.curs_set(False)

    # create game class
    test = game.Game()

    # init blueprints
    test.init_blueprints()

    # init test game map
    test.init_game_map(50, 50)
    game_map.create_map(game=test, level=1)

    # init test player
    player_b = {"name": "player", "char": [["@", "white", "green"]],
                "movement_cost": 15,
                "unpassable": True,
                "update_fov": True,
                "FOV": {"range": 10, "can_see": set()}}

    test.init_player(player_b)

    player_pos = (test.
                  pool.
                  entities[random.choice(test.game_map["rooms"])]["center"])
    test.place_entity(pos=player_pos,
                      entity_id=test.player_id,
                      add_pos_comp=True)
    test.pointer_pos = player_pos

    # TODO remove this
    pad = curses.newwin(24, 80, 1, 1)

    # load confif file
    test.load_config("config.json")

    # init systems
    test.pool.add_system(system=systems.move.MoveSystem,
                         name="move",
                         layer=2)
    test.pool.add_system(system=systems.fov.Fov,
                         name="fov",
                         layer=3)
    test.pool.add_system(system=systems.perform.Perform,
                         name="perform",
                         layer=0)
    test.pool.add_system(system=systems.simple_ai.Simple_Ai_System,
                         name="simple_ai",
                         layer=1)

    # welceome log msg
    test.log.append("Welcome!")
    test.log.append("Use the vi keys or the numpad to move")

    # TODO change pad to screen
    pad.timeout(test.config["debug"]["keyboard_timeout"])

    test.pool.update(["fov"])

    # game loop
    while test.state != "exit":
        test.perform_render(screen)
        key = pad.getch()

        if key >= 0 and not test.player.get("Perform"):
            test.perform_input(chr(key))

        while test.player.get("Perform"):
            test.pool.update()
            test.round += 1


# start main function
if __name__ == "__main__":
    curses.wrapper(main)

# say good bye
print("Thank you for playing pyaar!")
print("Good Bye!")
