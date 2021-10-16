from __future__ import annotations
import math
from fractions import Fraction
from typing import Iterator, Tuple, Optional, Any
import threading
import time

import ecs


# implementation of https://www.albertford.com/shadowcasting/

class Quarant:

    N: int = 0
    E: int = 1
    S: int = 2
    W: int = 3

    def __init__(
            self,
            cardinal: int,
            origin: Tuple[int, int]
            ) -> None:

        self.cardinal: int = cardinal

        self.oy: int
        self.ox: int
        self.oy, self.ox = origin

    def transform(self, tile: Tuple[int, int] ) -> Tuple[int, int]:

        y: int
        x: int
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
                 start_slope: Fraction,
                 end_slope: Fraction) -> None:
        self.depth: int = depth
        self.start_slope: Fraction = start_slope
        self.end_slope: Fraction = end_slope

    def tiles(self) -> Iterator[Tuple[int, int]]:
        min_x: int = round_ties_up(self.depth * self.start_slope)
        max_x: int = round_ties_down(self.depth * self.end_slope)
        x: int
        for x in range(min_x, max_x + 1):
            yield self.depth, x

    def next(self) -> Row:
        return Row(self.depth + 1,
                   self.start_slope,
                   self.end_slope)


def slope(tile: Tuple[int, int]) -> Fraction:
    y: int
    x: int
    y, x = tile
    return Fraction(2 * x - 1, 2 * y)


def is_symmetric(row: Row,
                 tile: Tuple[int, int]) -> bool:
    x: int
    _, x = tile
    return (x >= row.depth * row.start_slope and
            x <= row.depth * row.end_slope)


def round_ties_up(n: Fraction) -> int:
    return math.floor(n + 0.5)


def round_ties_down(n: Fraction) -> int:
    return math.ceil(n - 0.5)


def calc_fov(ori: Tuple[int, int], tile_map: dict[str, Any], entities: dict[int, dict[str, Any]]) -> set[Tuple[int, int]]:

    py: int
    px: int
    py, px = ori

    fov: set[Tuple[int, int]] = set()
    fov.add((py, px))

    i: int
    for i in range(4):

        quadrant: Quarant = Quarant(i, (py, px))

        first_row: Row = Row(1, Fraction(-1), Fraction(1))

        rows: list[Row] = [first_row]

        while rows:

            row: Row = rows.pop()

            #if row.depth > fov_range:
            #    break

            prev_tile: Optional[Tuple[int, int]] = None

            pt_id: int = 0
            t_id: int = 0

            tile: Tuple[int, int]
            for tile in row.tiles():

                if prev_tile:
                    pty: int
                    ptx: int
                    pty, ptx = quadrant.transform(prev_tile)
                    pt_id = tile_map["map_array"][pty][ptx][-1]

                ty: int
                tx: int
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


    lock = threading.Lock()

    class FovThread(threading.Thread):

        def __init__(self,
                     ent_id: int,
                     pos: Tuple[int, int],
                     tile_map: dict,
                     pool: ecs.Pool):
            threading.Thread.__init__(self)
            self.ent_id: int = ent_id
            self.ent_pos: Tuple[int, int] = pos
            self.tile_map: dict = tile_map
            self.pool: ecs.Pool = pool

        def run(self) -> None:
            Fov.lock.acquire()
            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                start_time: float = time.time()
            fov_set: set[Tuple[int, int]]
            fov_set = calc_fov(ori=self.ent_pos,
                               tile_map=self.tile_map,
                               entities=self.pool.entities)
            self.pool.entities[self.ent_id]["FOV"] = fov_set
            self.pool.remove_component_from_entity("update_fov", self.ent_id)
            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                end_time: float = time.time()
                d_time: float = end_time - start_time
                mgs0: str = f" | | FovSystem was completed for an entity with the id: {self.ent_id} in {d_time} seconds"
                self.pool.etc["game"].debug_log.add(mgs0)
            Fov.lock.release()

    def update(self):

        threads: list[Fov.FovThread] = []

        
        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            start_time: float = time.time()
            cycle: int = self.pool.etc["game"].round
            self.pool.etc["game"].debug_log.add("###")
            mgs0: str = f" | UpdateCycle: {cycle} :: FovSystem started"
            self.pool.etc["game"].debug_log.add(mgs0)
            self.pool.etc["game"].debug_log.add("----")
            
        ent_id: int
        for ent_id in self.act_on(["FOV", "update_fov", "pos"]):
            ent: dict[str, Any]
            ent = self.entities[ent_id]
            py: int
            px: int
            map_id: int
            py, px, map_id = ent["pos"]
            tile_map: dict[str, Any] = self.entities[map_id]
            threads.append(Fov.FovThread(ent_id=ent_id,
                                         pos=(py, px),
                                         tile_map=tile_map,
                                         pool=self.pool))
        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            if threads == []:
                self.pool.etc["game"].debug_log.add(" | | I had nothing to do!")

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            end_time: float = time.time()
            d_time: float = end_time - start_time
            mgs0: str = f" | UpdateCycle: {cycle} :: FovSystem finished in {d_time} seconds"
            self.pool.etc["game"].debug_log.add("----")
            self.pool.etc["game"].debug_log.add(mgs0)

