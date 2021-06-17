from __future__ import annotations
import random
from typing import Tuple, Iterator

import game
from mytpyes import Vec2int
import helpers.tilemap


class Rect_Room:

    def __init__(self,
                 y_pos: int, x_pos: int,
                 height: int, width: int):
        self.y_1 = y_pos
        self.y_2 = y_pos + height
        self.x_1 = x_pos
        self.x_2 = x_pos + width

    def intersect(self, other: Rect_Room) -> bool:
        return (self.y_1 <= other.y_2 and self.y_2 >= other.y_1 and
                self.x_1 <= other.x_2 and self.x_2 >= other.x_1)

    @property
    def center(self) -> Vec2int:
        center_y = (self.y_1 + self.y_2) // 2
        center_x = (self.x_1 + self.x_2) // 2
        return center_y, center_x

    @property
    def inside(self) -> Tuple[range, range]:
        return (range(self.y_1 + 1, self.y_2 - 1),
                range(self.x_1 + 1, self.x_2 - 1))


def create_horizontal_tunnel_part(start: Vec2int,
                                  end: Vec2int,
                                  size: int) -> Iterator[Vec2int]:
    start_y, start_x = start
    _, end_x = end
    tunnel_size = size // 2
    for tunnel_x in range(min(start_x, end_x),
                          max(start_x, end_x)):
        for tunnel_y in range(start_y - tunnel_size,
                              start_y + tunnel_size):
            yield tunnel_y, tunnel_x


def create_vertical_tunnel_part(start: Vec2int,
                                end: Vec2int,
                                size: int) -> Iterator[Vec2int]:
    start_y, _ = start
    end_y, end_x = end
    tunnel_size = size // 2
    for tunnel_y in range(min(start_y, end_y),
                          max(start_y, end_y)):
        for tunnel_x in range(end_x - tunnel_size,
                              end_x + tunnel_size):
            yield tunnel_y, tunnel_x


def create_simple_tunnel(start: Vec2int,
                         end: Vec2int,
                         size: int) -> Iterator[Vec2int]:

    if random.randint(0, 1):
        tunnel = [tunnel_coord for tunnel_coord
                  in create_horizontal_tunnel_part(start, end, size)]
        tunnel.extend([tunnel_coord for tunnel_coord
                       in create_vertical_tunnel_part(start, end, size)])
    else:
        tunnel = [tunnel_coord for tunnel_coord
                  in create_vertical_tunnel_part(start, end, size)]
        tunnel.extend([tunnel_coord for tunnel_coord
                       in create_horizontal_tunnel_part(start, end, size)])
    for tunnel_coord in tunnel:
        yield tunnel_coord


def cell_auto(game: game.Game,
              wall, floor):
    tilemap = game.game_map["map_array"]
    for y in range(game.game_map["map_height"]):
        for x in range(game.game_map["map_width"]):
            neighbours = helpers.tilemap.get_neighbours_2d(tilemap, (y, x))
            wall_count = 0
            for neighbour in neighbours:
                ny, nx = neighbour
                try:
                    e = game.pool.entities[tilemap[ny][nx][-1]]
                except IndexError:
                    raise IndexError(f"{neighbour} {tilemap[ny][nx]}")

                if e.get("map_tile"):
                    if e.get("wall"):
                        wall_count += 1
            if wall_count > 4:
                game.erase_entities((y, x))
                game.place_entity((y, x), entity_id=random.choice(wall))
                if ((y, x) in game.pool.entities[game.game_map_id]
                                                ["floor_tiles"]):
                    (game.pool.entities[game.game_map_id]
                                       ["floor_tiles"].remove((y, x)))
            if wall_count <= 3:
                game.erase_entities((y, x))
                game.place_entity((y, x), entity_id=random.choice(floor))
                game.pool.entities[game.game_map_id]["floor_tiles"].add((y, x))


def create_room_map(game: game.Game,
                    rooms: Vec2int,
                    rooms_height: Vec2int,
                    rooms_width: Vec2int,
                    wall_tiles: list,
                    floor_tiles: list) -> None:

    room_place_iterations = random.randint(rooms[0], rooms[1])

    min_room_height, max_room_height = rooms_height
    min_room_width, max_room_width = rooms_width

    tile_map = game.game_map

    for y in range(tile_map["map_height"]):
        for x in range(tile_map["map_width"]):
            game.place_entity(entity_id=random.choice(wall_tiles), pos=(y, x))

    room_list = list()

    for _ in range(room_place_iterations):

        room_height = random.randint(min_room_height, max_room_height)
        room_width = random.randint(min_room_width, max_room_width)

        room_y_pos = random.randint(2,
                                    tile_map["map_height"] - room_height - 2)
        room_x_pos = random.randint(2,
                                    tile_map["map_width"] - room_width - 2)

        new_room = Rect_Room(y_pos=room_y_pos, x_pos=room_x_pos,
                             height=room_height, width=room_width)

        if not rooms:
            rooms.append(new_room)
        else:
            if not any([new_room.intersect(other) for other in room_list]):
                room_list.append(new_room)

    for room in room_list:
        y_range, x_range = room.inside
        room_entity_blueprint = {"top_left_corner": (room.y_1, room.x_1),
                                 "top_right_corner": (room.y_1, room.x_2),
                                 "bottom_left_corner": (room.y_2, room.x_1),
                                 "bottom_right_corner": (room.y_2, room.x_2),
                                 "inside": (list(y_range), list(x_range)),
                                 "center": room.center}
        room_entity = game.pool.add_entity(room_entity_blueprint)
        game.pool.entities[game.game_map_id]["rooms"].append(room_entity)
        game.pool.entities[game.game_map_id]["floor_tiles"] = set()

    for room in room_list:
        y_range, x_range = room.inside
        for y in y_range:
            for x in x_range:
                game.erase_entities((y, x))
                game.place_entity(pos=(y, x),
                                  entity_id=random.choice(floor_tiles))
                game.pool.entities[game.game_map_id]["floor_tiles"].add((y, x))

        tunnel_start = room.center
        tunnel_end = random.choice(room_list).center

        while tunnel_end == tunnel_start:
            tunnel_end = random.choice(room_list).center

        for tunnel_coord in create_simple_tunnel(tunnel_start, tunnel_end, 2):
            game.erase_entities(tunnel_coord)
            game.place_entity(pos=tunnel_coord,
                              entity_id=random.choice(floor_tiles))


def place_nonactors(game: game.Game,
                    entities: list,
                    iter: int,
                    uniq: bool = False,
                    create_pos: bool = False) -> None:

    for _ in range(iter):
        if entities:
            coord = (random.choice(list(game.pool.entities[game.game_map_id]
                                                          ["floor_tiles"])))
            entity = random.choice(entities)
            if create_pos:
                y, x = coord
                pos = {"pos":( y, x, game.game_map_id)}
                game.pool.add_components_to_entity(pos, entity)
            game.place_entity(pos=coord, entity_id=entity, add_pos_comp=create_pos)
            game.pool.entities[game.game_map_id]["floor_tiles"].remove(coord)
            if uniq:
                entities.remove(entity)


def create_map(game: game.Game, level: int) -> None:

    game.game_map["path_nodes"] = dict()
    for my in range(game.game_map["map_height"]):
        for mx in range(game.game_map["map_width"]):
            game.game_map["path_nodes"][(my, mx)] = dict()
            neighbours = helpers.tilemap.get_neighbours_2d(pos=(my, mx),
                                                           array=game.game_map["map_array"])

            game.game_map["path_nodes"][(my, mx)]["neighbours"] = dict()
            game.game_map["path_nodes"][(my, mx)]["parent"] = dict()
            game.game_map["path_nodes"][(my, mx)]["neighbours"] = neighbours

    if level == 1:
        wall = [game.create_entity(chapter="map_tiles",
                                   blueprint="test_wall")]
        floor = [game.create_entity(chapter="map_tiles",
                                    blueprint="test_floor")]
        trees = [game.create_entity(chapter="map_tiles",
                                    blueprint="test_iron_tree"),
                 game.create_entity(chapter="map_tiles",
                                    blueprint="test_copper_tree")]
        stones = [game.create_entity(chapter="map_tiles",
                                     blueprint="boulder")]
        actors = [game.create_entity(chapter="test_actors",
                                     blueprint="bored_rat") for _ in range(10)]
        create_room_map(game=game,
                        rooms=(45, 75),
                        rooms_height=(5, 10),
                        rooms_width=(5, 10),
                        wall_tiles=wall,
                        floor_tiles=floor)
        cell_auto(game=game,
                  wall=wall,
                  floor=floor)
        place_nonactors(game=game, entities=trees, iter=45)
        place_nonactors(game=game, entities=stones, iter=10)
        place_nonactors(game=game, entities=actors, uniq=True, iter=10, create_pos=True)
