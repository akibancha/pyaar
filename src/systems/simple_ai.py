import random
import threading
import time

from typing import Tuple
import ecs


def manhattan_distance(start: Tuple[int, int], end: Tuple[int, int]) -> int:
    start_y, start_x = start
    end_y, end_x = end
    return abs(start_y - end_y) + abs(start_x - end_x)


def a_star(game,
           start_pos: Tuple[int, int],
           target_pos: Tuple[int, int]
):

    # TODO fix pathfinding
    game_map = game.game_map
    path_nodes = game_map["path_nodes"]

    start_y, start_x = start_pos
    end_y, end_x = target_pos

    step_dict = {}
    heu_dict = {}
    parent_dict = {}

    open_list = list()
    closed_list = list()

    step_dict[start_pos] = 0

    heu_dict[start_pos] = manhattan_distance(start_pos, target_pos)

    open_list.append(start_pos)

    while open_list:
        current_point: Tuple[int, int] = min(open_list, key=heu_dict.get)
        closed_list.append(current_point)
        open_list.remove(current_point)

        if current_point == target_pos:
            path = []
            while current_point != start_pos:
                path.append(current_point)
                current_point = parent_dict[current_point]
            return path

        for neighbour in game_map["path_nodes"][current_point]["neighbours"]:
            neighbour_y, neighbour_x = neighbour
            for entity_id in game_map["map_array"][neighbour_y][neighbour_x]:
                if game.pool.entities[entity_id].get("blocks_path"):
                    break
            else:
                steps = step_dict[current_point] + 1
                if neighbour in open_list:
                    if step_dict[neighbour] > steps:
                        step_dict[neighbour] = steps
                        parent_dict[neighbour] = current_point
                elif neighbour not in closed_list:
                    step_dict[neighbour] = steps
                    heu_dict[neighbour] = steps + manhattan_distance(
                        neighbour,
                        target_pos
                    )
                    parent_dict[neighbour] = current_point
                    open_list.append(neighbour)


class SimpleAiSystem(ecs.System):

    testlock = threading.Lock()

    class PFThread(threading.Thread):

        def __init__(self, ent_id, spos, tpos, pool):
            threading.Thread.__init__(self)
            self.ent_id = ent_id
            self.spos = spos
            self.tpos = tpos
            self.pool = pool

        def run(self):

            SimpleAiSystem.testlock.acquire()
            start_time = time.time()
            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                mgs0 = f" | | | <entity {self.ent_id}> will try to find a path towards the player."
                self.pool.etc["game"].debug_log.add(mgs0)

            path = a_star(game=self.pool.etc["game"],
                          start_pos=self.spos,
                          target_pos=self.tpos)
            if path:
                ty, tx = self.tpos
                sy, sx = self.spos
                py, px = path[-1]

                velo = {"velo": (py - sy, px - sx)}
                if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | | <entity {self.ent_id}> did find a path towards the player."
                    self.pool.etc["game"].debug_log.add(mgs0)
                    self.pool.etc["game"].debug_log.add(f" | | | <entity {self.ent_id}> path: {path}")
                    self.pool.etc["game"].debug_log.add(f" | | | <entity {self.ent_id}> will try to move to {py, px}")


            else:
                velo = {"velo": (random.randint(-1, 1),
                                 random.randint(-1, 1))}
                if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | | <entity {self.ent_id}> did not find a path towards the player, it will move in a random direction instead. {velo}"
                    self.pool.etc["game"].debug_log.add(mgs0)
                    self.pool.etc["game"].debug_log.add(" | |")
            movement_cost = self.pool.entities[self.ent_id].get("movement_cost")
            perform = {"Perform": {"round": (0, movement_cost),
                       "components": velo}}

            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | | <entity {self.ent_id}> pathfinding finished in {time.time() - start_time} seconds."
                    self.pool.etc["game"].debug_log.add(mgs0)
                    self.pool.etc["game"].debug_log.add(" | |")
            self.pool.add_components_to_entity(perform, self.ent_id)
            SimpleAiSystem.testlock.release()

    def update(self):

        player_ent = self.pool.etc["game"].player
        player_pos = player_ent.get("pos")

        if player_pos:
            player_pos = (player_pos[0], player_pos[1])
        else:
            return

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            global_start_time: float = time.time()
            cycle: int = self.pool.etc["game"].round
            self.pool.etc["game"].debug_log.add("###")
            mgs0: str = f" | UpdateCycle: {cycle} :: SimpleAiSystem started"
            self.pool.etc["game"].debug_log.add(mgs0)
            self.pool.etc["game"].debug_log.add(" | | ")


        threads = []
        can_not_see = []

        for entity_id in self.act_on(["simple_ai", "FOV",
                                      "pos", "movement_cost"]):

            ent = self.entities[entity_id]

            if ent.get("Perform"):
                continue

            ent_fov = ent.get("FOV")
            ent_pos = ent.get("pos")
            ey, ex, _ = ent_pos

            if player_pos in ent_fov:

                if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | <entity {entity_id}> can see the player. It will try to move towards the player or attack them."
                    self.pool.etc["game"].debug_log.add(mgs0)
                threads.append(SimpleAiSystem.PFThread(ent_id=entity_id,
                                                         spos=(ey, ex),
                                                         tpos=player_pos,
                                                         pool=self.pool))

            else:
                can_not_see.append(entity_id)
                velo = {"velo": (random.randint(-1, 1), random.randint(-1, 1))}
                if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | <entity {entity_id}> can not see the player. It will try to move in a random direction: {velo}"
                    self.pool.etc["game"].debug_log.add(mgs0)
                    self.pool.etc["game"].debug_log.add(" | |")
                perform = {"Perform": {"round": (0, 20),
                           "components": velo}}
                self.pool.add_components_to_entity(perform, entity_id)

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            if threads == [] and can_not_see == []:
                self.pool.etc["game"].debug_log.add(" | | I had nothing to do!")
                self.pool.etc["game"].debug_log.add(" | | ")

        if threads:
            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                self.pool.etc["game"].debug_log.add(" | |")
                mgs0 = f" | | pathfinding threads will be started:"
                self.pool.etc["game"].debug_log.add(mgs0)
                self.pool.etc["game"].debug_log.add(" | |")
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            mgs0: str = f" | UpdateCycle: {cycle} :: FovSystem finished in {time.time() - global_start_time} seconds."
            self.pool.etc["game"].debug_log.add(mgs0)
            self.pool.etc["game"].debug_log.add(" |")
