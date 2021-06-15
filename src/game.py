import json
import os
from typing import Optional

import ecs
import init_colors
from mytpyes import Vec2int
import interface.render_map
import interface.window
import interface.debug
import interface.input
import interface.render_log


class Game:

    def __init__(self):
        self.pool: ecs.Pool = ecs.Pool("game")
        self.game_map = None
        self.game_map_id = None
        self.player = None
        self.player_id = 0
        self.blueprints = None
        self.base_windows = dict()
        self.config = dict()
        self.state = "normal"
        self.round = 0
        self.log = list()
        self.colors = init_colors.create_color_book()
        self.pool.etc["game"] = self
        self.pointer_pos = None
        self.pointer_bound = True
        self.pent = None

    def init_game_map(self,
                      height: int,
                      width: int) -> None:

        game_map = {"map_array": [[[] for _ in range(width)]  # x list
                                  for _ in range(height)],       # y list
                    "map_height": height,
                    "map_width": width,
                    "rooms": list(),
                    "game_map": True}

        self.game_map_id = self.pool.add_entity(game_map)
        self.game_map = self.pool.entities[self.game_map_id]

    def init_player(self,
                    player_blueprint) -> None:
        self.player_id = self.pool.add_entity(player_blueprint)
        self.player = self.pool.entities[self.player_id]
        self.pent = self.player_id

    def save_player(self) -> None:
        if not os.path.exists("saves"):
            os.mkdir("saves")
        save_name = self.player["name"]
        with open("saves/" + save_name, "w") as f:
            json.dump(self.player, f)

    def create_entity(self,
                      chapter: str,
                      blueprint: str) -> int:
        return self.pool.add_entity(self.blueprints[chapter][blueprint])

    def place_entity(self,
                     pos: Vec2int,
                     entity_id: Optional[int] = None,
                     chapter: Optional[str] = None,
                     blueprint: Optional[str] = None,
                     add_pos_comp: Optional[bool] = False) -> Optional[int]:

        pos_y, pos_x = pos
        pos_c = {"pos": (pos_y, pos_x, self.game_map_id)}

        if entity_id:
            self.game_map["map_array"][pos_y][pos_x].append(entity_id)
            if add_pos_comp:
                self.pool.add_components_to_entity(pos_c, entity_id)
        elif chapter and blueprint:
            entity_id = self.create_entity(chapter, blueprint)
            self.game_map["map_array"][pos_y][pos_x].append(entity_id)
            if add_pos_comp:
                self.pool.add_components_to_entity(pos_c, entity_id)
            return entity_id

    def erase_entities(self,
                       pos: Vec2int) -> None:
        pos_y, pos_x = pos
        self.game_map["map_array"][pos_y][pos_x] = list()

    def erase_entity(self,
                     entity_id: int,
                     pos: Optional[Vec2int] = None) -> None:
        if pos:
            pos_y, pos_x = pos
            self.game_map["map_array"][pos_y][pos_x].remove(entity_id)
        else:
            for pos_y in range(self.game_map["map_height"]):
                for pos_x in range(self.game_map["map_width"]):
                    self.game_map["map_array"][pos_y][pos_x].remove(entity_id)

    def load_player(self,
                    name) -> None:
        with open("saves/" + name, "r") as f:
            player_blueprint = json.load(f)
        self.init_player(player_blueprint)

    def perform_input(self, key):

        interface.input.handle_input(self, key)

    def perform_render(self, screen):

        if self.pointer_bound:
            py, px, _ = self.player["pos"]
            self.pointer_pos: Vec2int = (py, px)

        if self.state in ("normal", "calc"):

            interface.window.render_resize_msg(min_size=(24, 80),
                                               screen=screen,
                                               frames=25)
            interface.window.set_base_windows(self, screen, True)
            interface.debug.render(game=self, window=self.base_windows["info"])
            interface.render_log.render(map_window=self.base_windows["log"],
                                        game=self)
            interface.render_map.render(game=self,
                                        map_window=self.base_windows["map"],
                                        fov=True,
                                        fov_entity=self.pent,
                                        pointer_pos=self.pointer_pos)

    def init_blueprints(self) -> None:
        self.blueprints = dict()
        for chapter in os.listdir("blueprints"):
            with open("blueprints/" + chapter, "r") as f:
                self.blueprints[chapter.replace(".json", "")] = json.load(f)

    def load_config(self,
                    config_file: str) -> None:

        with open(config_file, "r") as config:
            self.config = json.load(config)

    def save_config(self,
                    config_file: str) -> None:
        with open(config_file, "w") as config:
            json.dump(self.config, config)
