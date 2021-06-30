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

    # load config file
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

    # welcome log msg
    test.log.append("Welcome!")
    test.log.append("Use the vi keys or the numpad to move")

    # set input timeout
    screen.timeout(test.config["debug"]["keyboard_timeout"])

    # init entity fovs
    test.pool.update(["fov"])

    # game loop
    while test.state != "exit":

        # render screen
        test.perform_render(screen)

        # get player input
        key = screen.getch()

        # test if there is a player input and ensures the player isn't
        # performing an action
        if key >= 0 and not test.player.get("Perform"):
            test.perform_input(chr(key))

        # update the pool while the player is performing an action
        # every update cycle equates to one ingame round
        while test.player.get("Perform"):
            test.pool.update()
            test.round += 1


# start main function
if __name__ == "__main__":
    curses.wrapper(main)

# say good bye
print("Thank you for playing pyaar!")
print("Good Bye!")
