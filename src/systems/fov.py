import math
from fractions import Fraction
from typing import Iterator
import threading

import ecs
import helpers.tilemap
from mytpyes import Vec2int


class Quarant:

    N = 0
    E = 1
    S = 2
    W = 3

    def __init__(self,
                 cardinal,
                 origin) -> None:
        self.cardinal = cardinal
        self.oy, self.ox = origin

    def transform(self,
                  tile) -> Vec2int:
        y, x = tile
        if self.cardinal == self.N:
            return self.oy - y, self.ox + x
        if self.cardinal == self.S:
            return self.oy + y, self.ox + x
        if self.cardinal == self.E:
            return self.oy + x, self.ox + y
        if self.cardinal == self.W:
            return self.oy + x, self.ox - y
        return 0, 0


class Row:

    def __init__(self,
                 depth: int,
                 start_slope,
                 end_slope) -> None:
        self.depth = depth
        self.start_slope = start_slope
        self.end_slope = end_slope

    def tiles(self) -> Iterator[Vec2int]:
        min_x = round_ties_up(self.depth * self.start_slope)
        max_x = round_ties_down(self.depth * self.end_slope)
        for x in range(min_x, max_x + 1):
            yield self.depth, x

    def next(self):
        return Row(self.depth + 1,
                   self.start_slope,
                   self.end_slope)


def slope(tile: Vec2int) -> Fraction:
    y, x = tile
    return Fraction(2 * x - 1, 2 * y)


def is_symmetric(row: Row,
                 tile: Vec2int) -> bool:
    y, x = tile
    return (x >= row.depth * row.start_slope and
            x <= row.depth * row.end_slope)


def round_ties_up(n) -> int:
    return math.floor(n + 0.5)


def round_ties_down(n) -> int:
    return math.ceil(n - 0.5)

def calc_fov(ori, tile_map, entities) -> set:

    py, px = ori
    fov = set()
    fov.add((py, px))

    for i in range(4):

        quadrant = Quarant(i, (py, px))

        first_row = Row(1, Fraction(-1), Fraction(1))

        rows = [first_row]

        while rows:

            row = rows.pop()

            #if row.depth > fov_range:
            #    break

            prev_tile = None

            for tile in row.tiles():

                if prev_tile:
                    pty, ptx = quadrant.transform(prev_tile)
                    pt_id = tile_map["map_array"][pty][ptx][-1]

                ty, tx = quadrant.transform(tile)

                if (ty not in range(tile_map["map_height"]) or
                   tx not in range(tile_map["map_width"])):
                    continue

                t_id = tile_map["map_array"][ty][tx][-1]

                if (entities[t_id].get("blocks_sight") or
                   is_symmetric(row, tile)):
                    fov.add((ty, tx))

                if prev_tile:

                    if (entities[pt_id].get("blocks_sight") and
                       not entities[t_id].get("blocks_sight")):
                        row.start_slope = slope(tile)

                    if (not entities[pt_id].get("blocks_sight")
                       and entities[t_id].get("blocks_sight")):
                        next_row = row.next()
                        next_row.end_slope = slope(tile)
                        rows.append(next_row)

                prev_tile = tile

            if prev_tile:

                pty, ptx = quadrant.transform(prev_tile)
                pt_id = tile_map["map_array"][pty][ptx][-1]

                if not entities[pt_id].get("blocks_sight"):
                    rows.append(row.next())

    return fov


class Fov(ecs.System):

    class FovThread(threading.Thread):

        def __init__(self, ent_id, pos, tile_map, ents):
            threading.Thread.__init__(self)
            self.ent_id = ent_id
            self.ent_pos = pos
            self.tile_map = tile_map
            self.pool = ents

        def run(self):
            fov_set = calc_fov(ori=self.ent_pos,
                               tile_map=self.tile_map,
                               entities=self.pool.entities)
            self.pool.entities[self.ent_id]["FOV"] = fov_set
            self.pool.remove_component_from_entity("update_fov", self.ent_id)


    def update(self):

        threads = []
        for ent_id in self.act_on(["FOV", "update_fov", "pos"]):
            ent = self.entities[ent_id]
            py, px, map_id = ent["pos"]
            tile_map = self.entities[map_id]
            threads.append(Fov.FovThread(ent_id=ent_id, pos=(py, px), tile_map=tile_map, ents=self.pool))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
