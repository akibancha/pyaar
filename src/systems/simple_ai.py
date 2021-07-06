import random
import threading

from typing import Tuple
import ecs


def a_star(game,
           start_pos: Tuple[int, int],
           target_pos: Tuple[int, int]):

    # TODO fix pathfinding
    game_map = game.game_map
    path_nodes = game_map["path_nodes"]
    # start node = start_pos
    # end node = target_pos
    start_y, start_x = start_pos
    end_y, end_x = target_pos
    g_dict = {node: float('inf') for node in path_nodes}
    f_dict = {node: float('inf') for node in path_nodes}
    open_list = list()
    closed_list = list()
    g_dict[start_pos] = 0
    f_dict[start_pos] = abs(start_y - end_y) + abs(start_x - end_x)
    open_list.append(start_pos)
    while open_list:
        current_node = min(open_list, key=f_dict.get)
        closed_list.append(current_node)
        open_list.remove(current_node)
        if current_node == target_pos:
            path = list()
            while current_node != start_pos:
                path.append(current_node)
                current_node = path_nodes[current_node]["parent"]
            return path
        cy, cx = current_node
        for neighbour in path_nodes[current_node]["neighbours"]:
            ny, nx = neighbour
            for meid in game_map["map_array"][ny][nx]:
                if game.pool.entities[meid].get("unpassable"):
                    break
                g = g_dict[current_node] + 1
                f = f_dict[current_node] = (g_dict[current_node] +
                                            abs(cy - end_y) + abs(cx - end_x))
                if neighbour in open_list:
                    if g_dict[neighbour] > g:
                        g_dict[neighbour] = g
                        path_nodes[neighbour]["parent"] = current_node
                if neighbour not in open_list and neighbour not in closed_list:
                    open_list.append(neighbour)
                    g_dict[neighbour] = g
                    f_dict[neighbour] = f
                    path_nodes[neighbour]["parent"] = current_node


class Simple_Ai_System(ecs.System):

    testlock = threading.Lock()

    class PFThread(threading.Thread):

        def __init__(self, ent_id, spos, tpos, pool):
            threading.Thread.__init__(self)
            self.ent_id = ent_id
            self.spos = spos
            self.tpos = tpos
            self.pool = pool

        def run(self):
            path = a_star(game=self.pool.etc["game"],
                          start_pos=self.spos,
                          target_pos=self.tpos)
            if path:
                sy, sx = self.spos
                py, px = path[-1]
                velo = {"velo": (py - sy, px - sx)}
            else:
                velo = {"velo": (random.randint(-1, 1),
                                 random.randint(-1, 1))}
            movemen_cost = self.pool.entities[self.ent_id].get("movement_cost")
            perform = {"Perform": {"round": (0, movemen_cost),
                       "components": velo}}
            self.pool.add_components_to_entity(perform, self.ent_id)

    def update(self):

        player_ent = self.pool.etc["game"].player
        player_pos = player_ent.get("pos")

        if player_pos:
            player_pos = (player_pos[0], player_pos[1])
        else:
            return

        threads = []

        for entity_id in self.act_on(["simple_ai", "FOV",
                                      "pos", "movement_cost"]):

            ent = self.entities[entity_id]

            if ent.get("Perform"):
                continue

            ent_fov = ent.get("FOV")
            ent_pos = ent.get("pos")
            ey, ex, _ = ent_pos

            if player_pos in ent_fov:
                threads.append(Simple_Ai_System.PFThread(ent_id=entity_id,
                                                         spos=(ey, ex),
                                                         tpos=player_pos,
                                                         pool=self.pool))

            else:
                velo = {"velo": (random.randint(-1, 1), random.randint(-1, 1))}
                perform = {"Perform": {"round": (0, 20),
                           "components": velo}}
                self.pool.add_components_to_entity(perform, entity_id)

        if threads:
            for t in threads:
                t.start()
            for t in threads:
                t.join()
