import curses
import random

import game_map
from game import Game

import systems


def main(screen) -> None:
    """
    The main function of this game.
    It Initializes the main components of the game and starts the game loop.

    :return None

    """

    # deactivate terminal cursor
    curses.curs_set(False)

    # create game class
    test = Game()

    # init blueprints
    test.init_blueprints()

    # init test game map
    test.init_game_map(height=50, width=50)

    game_map.create_map(game=test, level=1)

    
    # load config file
    test.load_config("config.json")

    # init systems
    test.pool.add_system(
        system=systems.MoveSystem,
        name="move",
        layer=2
    )
    test.pool.add_system(
        system=systems.FovSystem,
        name="fov",
        layer=4
    )
    test.pool.add_system(
        system=systems.PerformSystem,
        name="perform",
        layer=0
    )
    test.pool.add_system(
        system=systems.SimpleAiSystem,
        name="simple_ai",
        layer=0
    )
    test.pool.add_system(
        system=systems.DmgSystem,
        name="dmg",
        layer=3
    )
    test.pool.add_system(
        system=systems.DieSystem,
        name="die",
        layer=4
    )

    weapon_id = test.create_entity("weapons", "old_axe")
    light_source_id = test.create_entity("light_sources", "old_torch")

    # init test player
    player_b = {
        "name": "Aki",
        "player": True,
        "inventory": {
            "slots": 4,
            "items": []
        },
        "equipment": {
            "weapon": None,
            "armor": None,
            "light_source": None
        },
        "char": [["@", "white", "green"]],
        "movement_cost": 10,
        "health": {"max_hp": 15, "current_hp":15},
        "dead_body": {"char": "ħ", "name": "The Body of"},
        "update_fov": True,
        "FOV": True,
        "actor": True
    }


    test.init_player(player_b)
    test.give_item(test.player_id, weapon_id) 
    test.give_item(test.player_id, light_source_id) 
    test.equip_item(test.player_id, light_source_id)
    test.equip_item(test.player_id, weapon_id)

    player_pos = (
        test.pool.entities[random.choice(test.game_map["rooms"])]["center"]
    )

    test.place_entity(
        pos=player_pos,
        entity_id=test.player_id,
        add_pos_comp=True
    )

    test.pointer_pos = player_pos

    # welcome log msg
    test.log.append("Welcome!")
    test.log.append("Use the vi keys or the numpad to move")

    # set input timeout
    screen.timeout(test.config["debug"]["keyboard_timeout"])

    # hardware character/line editing
    screen.idlok(test.config["options"]["enable_idlok"])
    screen.idcok(test.config["options"]["enable_idcok"])

    # init entity fovs
    test.debug_log.add(":: init entity fovs ::")
    test.pool.update(systems=["fov"])


    test.pointer_bound = True
    test.pointer_entity = test.player_id

    # game loop
    while test.state != "exit":

        if test.player.get("dead"):
            test.state = "game_over"
        # render screen
        test.perform_render(screen)

        # get player input
        key: int
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


if __name__ == "__main__":
    curses.wrapper(main)

print("Thank you for playing pyaar!")
print("Good Bye!")
