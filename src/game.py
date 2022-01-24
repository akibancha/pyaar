from __future__ import annotations
import json
import os
from typing import Optional, Tuple, List, Any

import ecs
import init_colors
import interface.render_map
import interface.window
import interface.debug
import interface.input
import interface.render_log
import entity_factory
import helpers.tilemap
import interface.game_over
import interface.info


class Game:

    def __init__(self):

        """

        Takes care of the main components of the game.

        ### Entity component system:
        This class initializes with a new entity component system which can
        be accessed via the pool attribute.

        ### Game map:
        After the game map was initialized, the attributes game_map and
        game_map_id will be set to reference the game map entity and
        game map entity id. Initialize the game map with the init_game_map
        method. Other parts of the game may try to access these attributes and
        raise a RuntimeError in case the game map was not initialized.

        ### Player:
        After the player was initialized, the attributes player and player_id
        will be set to reference the player entity and the player entity
        id. Initialize the player entity with the init_player method. Other
        parts of the game may try to access these attributes and raise a
        RuntimeError in case the player entity was not initialized.

        ### Blueprints:
        After the blueprint book was initialized, the blueprint book can be
        accessed via the blueprints attribute. Initialize the blueprint book
        with the init_blueprints method. Other parts of the game may try to
        access this attribute and raise a RuntimeError in case it the blueprint
        book was not initialized. See the doc string of the init_blueprints
        method to learn more about the structure of the blueprint book.

        ### Curses windows:
        The render method will create the curses windows for the game map, the
        log and the player information and saves them to a dictionary which can
        be accessed via the base_windows attribute.

        ### Config:
        After a config file was loaded, the created dictionary can be accessed
        via the config attribute. Load a config file with the load_config
        method.
        Other parts of the game may try to access this attribute and raise a
        RuntimeError in case no config file was loaded. Config files should be
        json files with keywords representing non static components of
        the game. TODO write doc for the config file.

        ### Game state:
        The attribute state consists of a string representing the current
        state of the game. This class initializes with the state "normal".
        Depending of the game state the render and perform_input methods will
        behave differently.
        If the state is set to "exit", the game will quit.
        TODO create set_game_state method, maybe replace
        the string with enums.

        ### Game rounds:
        The attribute round consists of an integer that is meant to track
        the number of the current ingame round. This attribute
        initializes with the value 0.

        ### Game Log:
        The attribute log consists of a list that should only contain strings.
        The here contained strings will be displayed in the log window while
        the game state is set to "normal".

        ### Terminal Colors:
        This class will initialize with a base set of eight colors that add up
        to a total of 64 color pair numbers which stored inside of a dictionary.
        These colors are: white, black, blue, yellow, red, green, magenta,
        cyan. The color pair numbers can be accessed via the colors attribute
        using keywords representing the background and foreground colors.
        Example: self.colors["white"]["black"] # first keyword = foreground,
        second keyword = background

        ### Map Pointer:
        The map pointer is the point on the map the camera is centered on.
        It consists of a tuple containing two integers which is stored
        in the pointer_pos attribute and is initially set to (0, 0).
        The attribute pointer_bound consists of a bool and is initially set to
        False. If it is set to True the camera will centered on the entity
        represented by the id stored in the pointer_entity attribute.
        """

        # empty entity pool
        self.pool: ecs.Pool = ecs.Pool("game")
        # the map entity
        self.game_map: Optional[dict] = None
        # the current id of map inside of the entity pool
        self.game_map_id: Optional[int] = None
        # player entity
        self.player: Optional[dict] = None
        # player entity id
        self.player_id: Optional[int] = None
        # entity blueprints
        self.blueprints: Optional[dict] = None
        # dict for all the curses windows
        self.base_windows: dict = dict()
        # config file
        self.config: Optional[dict] = None
        # current game state
        self.state: str = "normal"
        # passed game rounds
        self.round: int = 0
        # game log
        self.log: List[str] = list()
        # game colors (8 base colors)
        self.colors: dict = init_colors.create_color_book()
        # reference to self from inside the pool
        self.pool.etc["game"] = self
        # position of the pointer
        self.pointer_pos: Tuple[int, int] = (0, 0)
        # the pointer bound to the player
        self.pointer_bound: bool = False
        # the entity focused by the pointer while bound
        self.pointer_entity: Optional[int] = None
        # log for debug mgs
        self.debug_log: interface.debug.DebugLog = interface.debug.DebugLog()

    def init_game_map(
        self,
        height: int,
        width: int
    ) -> None:
        """
        This method initializes the game map. It creates the game map entity inside of
        self.pool and sets self.game_map and self.game_map_id to reference it.


        Parameters
        ----------
        height: int
            The height of the game map.
        width: int
            The width of the game map.
        """

        # define map entity
        game_map: dict[str, list|int|bool]
        game_map = {
            # empty 2d list
            # will hold a list of entity ids: int for every (y, x) position
            # List[List[int]]
            "map_array": [[[] for _ in range(width)]  # x list
                          for _ in range(height)],  # y list
            # map height:int and width: int
            "map_height": height,
            "map_width": width,
            # a list of rooms that exist on the map
            "rooms": list(),
            # entity is a game map
            # not used TODO remove
            "game_map": True
        }

        # create map entity and references to the map entity and it's id
        self.game_map_id = self.pool.add_entity(game_map)
        self.game_map = self.pool.entities[self.game_map_id]

    def init_player(
        self,
        player_blueprint: dict
    ) -> None:

        # TODO make it compatible with the blueprint book
        """
        This method initializes the player. It creates the player entity inside of self.pool.entities
        and sets self.player and self.player_id to reference it.

        Parameters
        ----------
        player_blueprint: dict
            The blueprint that should be used to create the player.
        """

        # create the player entity and references to the entity and it's id
        self.player_id = self.pool.add_entity(player_blueprint)
        self.player = self.pool.entities[self.player_id]

    def create_entity(
        self,
        chapter: str,
        blueprint: str
    ) -> int:

        """
        This method uses a blueprint from the blueprint book to create
        an entity inside of self.pool.entities

        Parameters
        ----------
        chapter: str
            The name of the chapter the blueprint is located in.
            (The json file inside ./blueprints)
        blueprint: str
            The name of the blueprint.
            (The keyword inside the json file)

        Returns
        -------
        entity_id: int
            This method returns the entity id of the created entity.
            Use this id to access the entity inside of self.pool.entities.

        Raises
        ------
        RuntimeError
            If the blueprint book was not initialized this method will
            raise an error.
        """

        if self.blueprints:
            forged_blueprint: dict = entity_factory.create_actor(
                self.blueprints[chapter][blueprint]
            )

            return self.pool.add_entity(forged_blueprint)
        else:
            raise RuntimeError(
                "No blueprint book was found.\n \
                    Initialize a blueprint book with .init_blueprints method"
            )

    def place_entity(
        self,
        pos: Tuple[int, int],
        entity_id: Optional[int] = None,
        chapter: Optional[str] = None,
        blueprint: Optional[str] = None,
        add_pos_comp: Optional[bool] = False
    ) -> Optional[int]:

        """
        This method will either place an already existing entity or newly created one on the game map.

        Parameters
        ----------
        pos: Tuple[int, int]
            The position coordinate the entity should be placed on.
        entity_id: Optional[int]
            The entity id of the entity you want to place. (In case you want to
            place an already existing entity)
        chapter: Optional[str]
            The chapter the blueprint that should be used to create the entity
            is located in.
        blueprint: Optional[str]
            The blueprint that should be used to create the entity
        add_pos_comp: Optional[bool]
            Set this to True in case you want to give a position component
            to the entity. This also updates the component of an
            existing entity in case it already has one.

        Returns
        -------
        entity_id: Optional[int]
            This method will return the entity id of the created entity.
            (In case you did create a new entity)
            Use this id to access the entity inside of self.pool.entities.

        Raises
        ------
        RuntimeError
            If the game map was not initialized a RuntimeError will be raised.
            If you are trying to use the blueprint book when it was not initialized yet a RuntimeError will be raised.
            If you are trying to place an entity on a nonexistent map coordinate a RuntimeError will be raised.
            If you are trying to place an entity with an id that does not exist inside of the entity pool a
            RuntimeError will be raised.
        """

        # create the position component
        pos_y, pos_x = pos
        pos_c: dict = {"pos": (pos_y, pos_x, self.game_map_id)}

        # check if there is a game map and raise a RuntimeError
        # if there isn't one
        if not self.game_map or not self.game_map_id:
            err_msg0 = "You are trying to place an entity on a nonexistent game map.\n"
            err_msg1 = "Please initialize the game map with the .init_game_map method"
            raise RuntimeError(err_msg0 + err_msg1)

        # check if the position coordinate exists on the game map
        map_height = self.game_map["map_height"]
        map_width = self.game_map["map_width"]
        if not helpers.tilemap.check_pos_exist(
            game=self,
            pos=pos
        ):
            err0 = f"You are trying to place an entity on the coordinate {pos}.\n"
            err1 = "This coordinate seems not to exist on the game map.\n"
            err2 = f"Your game map:\nheight={map_height},\nwidth={map_width}"
            raise RuntimeError(err0 + err1 + err2)

        # check if a existing entity should be placed
        if entity_id:

            # check if the entity id exists in the entity pool
            if not self.pool.check_for_entity_id(entity_id=entity_id):
                err0 = f"You are trying to place an entity with the id: {entity_id}.\n"
                err1 = "This entity id was not found in the entity pool"
                raise RuntimeError(err0 + err1)

            # add entity id to the map array
            self.game_map["map_array"][pos_y][pos_x].append(entity_id)
            # add the position component in case it should be added
            if add_pos_comp:
                self.pool.add_components_to_entity(pos_c, entity_id)

        # check if a chapter and a blueprint were given
        elif chapter and blueprint:
            # check if the the blueprint book was initialized
            if not self.blueprints:
                err0 = "You are trying to create an entity but the blueprint book was not initialized yet.\n"
                err1 = "Please initialize the blueprint book with the init_blueprints method"
                raise RuntimeError(err0 + err1)

            # create entity from the blueprint book
            entity_id = self.create_entity(chapter, blueprint)
            # add the id to the map array
            self.game_map["map_array"][pos_y][pos_x].append(entity_id)
            # add the position component in case it should be added
            if add_pos_comp:
                self.pool.add_components_to_entity(pos_c, entity_id)
            # return the id of the created entity
            return entity_id

    def erase_entities(
        self,
        pos: Tuple[int, int]
    ) -> None:
        """
        This method will erase all entities within a given coordinate from the game map.

        Parameters
        ----------
        pos: Tuple[int, int]
         The position coordinate you want to erase. (y, x)

        Raises
        ------
        RuntimeError
            If the position coordinate you want to erase does not exist on the game map a RuntimeError will be raised.
        """

        pos_y, pos_x = pos

        # check if the position coordinate exists on the game map
        map_height = self.game_map["map_height"]
        map_width = self.game_map["map_width"]
        if not helpers.tilemap.check_pos_exist(
            game=self,
            pos=pos
        ):
            err0 = f"You are trying to erase the position coordinate {pos}.\n"
            err1 = "This coordinate does not to exist on the game map.\n"
            err2 = f"Your game map:\nheight={map_height},\nwidth{map_width}"
            raise RuntimeError(err0 + err1 + err2)

        # create an empty list on this coordinate
        self.game_map["map_array"][pos_y][pos_x] = list()

    def erase_entity(
        self,
        entity_id: int,
        pos: Optional[Tuple[int, int]] = None
    ) -> None:

        """
        This method will either erase an entity from the game map completely or erase it from
        a given position coordinate.
        The entity will only be erased from the game map. It will still exist inside of the pool.

        Parameters
        ----------
        entity_id: int
            The id of the entity that should be erased.
        pos: Tuple[int, int], Optional
            The position coordinate the entity should be erased from.

        Raises
        ------
        RuntimeError
            If you are trying to use a position coordinate that does not exist on the game map a RuntimeError will
            be raised.

        """

        # check if the entity should be erased from a specific coordinate
        if pos:
            pos_y, pos_x = pos
            map_height = self.game_map["map_height"]
            map_width = self.game_map["map_width"]
            # check if the position coordinate exist on the game map
            if not helpers.tilemap.check_pos_exist(
                game=self,
                pos=pos
            ):
                err0 = f"You are trying to erase the entity (id={entity_id}) from the position coordinate {pos}.\n"
                err1 = "This coordinate does not exist on your game map.\n"
                err2 = f"Your game map:\nHeight={map_height},\nWidth={map_width}"
                raise RuntimeError(err0 + err1 + err2)

            # erase the entity from the coordinate
            self.game_map["map_array"][pos_y][pos_x].remove(entity_id)
        # iterate through the whole map
        else:
            for pos_y in range(self.game_map["map_height"]):
                for pos_x in range(self.game_map["map_width"]):
                    # check if the entity exists here
                    if entity_id in self.game_map["map_array"][pos_y][pos_x]:
                        # erase the entity from the coordinate
                        self.game_map["map_array"][pos_y][pos_x].remove(entity_id)

    def perform_input(
        self,
        key: str
    ) -> None:

        """
        This method handles the player input.

        Parameters
        ----------
        key: str
           The str representation of the pressed key.

        """
        # process input
        interface.input.handle_input(
            game=self,
            key=key
        )

    def perform_render(
        self,
        screen
    ) -> None:

        """
        This method handles the rendering of game depending on the game state.

        Parameters
        ----------
        screen
            The curses standard screen
        """

        # check if the pointer position should be bound to the player position
        if self.pointer_bound:
            # unzip player pos
            # TODO remove third value
            py, px, _ = self.player["pos"]
            # set the pointer position to the player position
            self.pointer_pos: Tuple[int, int] = (py, px)

        # check for the game states
        if self.state in "normal":
            # check for minimal screen size
            interface.window.render_resize_msg(
                min_size=(24, 80),
                screen=screen,
                frames=25
            )

            # create base windows
            interface.window.set_base_windows(
                game=self,
                screen=screen,
                refresh=True
            )

            # render the log window
            interface.render_log.render(
                map_window=self.base_windows["log"],
                game=self
            )

            # render the map window
            interface.render_map.render(
                game=self,
                map_window=self.base_windows["map"],
                fov=True,
                fov_entity=self.pointer_entity,
                pointer_pos=self.pointer_pos
            )
            interface.info.render_info_window(
                window=self.base_windows["info"],
                game=self
            )

            
        elif self.state == "game_over":
            interface.window.render_resize_msg(
                min_size=(24, 80),
                screen=screen,
                frames=60
            )
            interface.window.set_base_windows(
                screen=screen,
                refresh=True,
                game=self
            )
            interface.render_log.render(
                map_window=self.base_windows["log"],
                game=self
            )
            interface.game_over.render_game_over(
                window=self.base_windows["map"],
                game=self
            )

    def init_blueprints(self) -> None:

        """
        This method initializes the blueprint book.
        """

        self.blueprints = dict()
        for chapter in os.listdir("blueprints"):
            with open("blueprints/" + chapter, "r") as f:
                chapter_str = chapter.replace(".json", "")
                self.blueprints[chapter_str] = json.load(f)
            for k, v in self.blueprints[chapter_str].items():
                v["chapter/blueprint"] = f"{chapter_str}/{k}"

    def load_config(
        self,
        config_file: str
    ) -> None:

        """
        """

        with open(config_file, "r") as config:
            self.config = json.load(config)

        max_debug_amount: int = self.config["debug"]["debug_log_mgs_amount"]
        self.debug_log.set_max_amount(max_debug_amount)

    def save_config(
        self,
        config_file: str
    ) -> None:

        """
        This method saves the 'config' attribute to a .json file.
        """
        with open(config_file, "w") as config:
            json.dump(self.config, config)
