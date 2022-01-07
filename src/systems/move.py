from typing import Any, Optional
import time

import ecs


class MoveSystem(ecs.System):

    def update(self):

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            mgs0 = f" | Update Cycle {self.pool.etc['game'].round} :: MoveSystem started"
            self.pool.etc["game"].debug_log.add(mgs0)
            global_start_time = time.time()
            cycle = self.pool.etc["game"].round

            if not self.act_on(["velo", "pos"]):
                self.pool.etc["game"].debug_log.add(" | | ")
                self.pool.etc["game"].debug_log.add(" | | I had nothing to do!")
                self.pool.etc["game"].debug_log.add(" | | ")


        for e_id in self.act_on(["velo", "pos"]):

            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                self.pool.etc["game"].debug_log.add(" | | ")

            ent = self.entities[e_id]

            vy, vx = ent["velo"]

            y, x, map_id = ent["pos"]

            dy, dx = vy + y, vx + x

            name = ent.get("name")

            if not name:
                name = f"<entity {e_id}>"

            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                mgs0 = f" | | <entity {e_id}> on pos: {(y, x)} attempts to move to target: {dy, dx} - velocity: {(vy, vx)}"
                self.pool.etc["game"].debug_log.add(mgs0)

            if (dy not in range(self.pool.etc["game"].game_map["map_height"]) or
                dx not in range(self.pool.etc["game"].game_map["map_width"])):
                if self.pool.etc["game"].config["debug"]["debug_log_msg_system_report"] is True:
                    mgs0 = f" | | <entity {e_id}> could not move to target: The target is not a valid point on the map."
                    self.pool.etc["game"].debug_log.add(mgs0)
                    self.pool.etc["game"].debug_log.add(" | ")
                return

            for ent_in in self.entities[map_id]["map_array"][dy][dx]:
                if self.entities[ent_in].get("player"):
                    self.pool.etc["game"].log.append(f"{name} wants some pets")
                    break

                if (self.entities[ent_in].get("blocks_path")
                    and not self.pool.etc["game"].config["debug"]["disable_collision"]
                    and not ent_in == e_id):

                    tile = self.entities[ent_in]
                    tile_name = tile.get("name")

                    log_role = "something"

                    if not tile_name:
                        tile_name = f"<entity {ent_in}>"

                    if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                        mgs0 = f" | | <entity {e_id}> could not move to target: The target is not passable."
                        self.pool.etc["game"].debug_log.add(mgs0)



                    log = f"{name} bumps into {log_role} ({tile_name})"

                    if (y, x) in self.pool.etc["game"].player["FOV"]:
                        self.pool.etc["game"].log.append(log)
                    break
            else:

                self.entities[e_id]["pos"] = (dy, dx, map_id)
                self.pool.entities[map_id]["map_array"][dy][dx].append(e_id)
                self.pool.entities[map_id]["map_array"][y][x].remove(e_id)
                if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                    mgs0 = f" | | <entity {e_id}> on pos: {(y, x)} was moved to target."
                    self.pool.etc["game"].debug_log.add(mgs0)

                if ent.get("FOV"):
                    self.pool.add_components_to_entity({"update_fov": True}, e_id)
                    if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                        mgs0 = f" | | <entity {e_id}> FOV will be updated in the next round."
                        self.pool.etc["game"].debug_log.add(mgs0)

            self.pool.remove_component_from_entity("velo", e_id)

            if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
                self.pool.etc["game"].debug_log.add(" | |")


        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            mgs0: str = f" | UpdateCycle: {cycle} :: MoveSystem finished in {time.time()- global_start_time} seconds"
            self.pool.etc["game"].debug_log.add(mgs0)
            self.pool.etc["game"].debug_log.add(" |")
