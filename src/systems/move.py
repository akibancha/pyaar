from typing import Any, Optional

import ecs


class MoveSystem(ecs.System):

    def update(self):

        if self.pool.etc["game"].config["debug"]["debug_log_mgs_system_report"] is True:
            mgs0: str = f" | Update Cycle {self.pool.etc['game'].round} :: MoveSystem started"
            self.pool.etc["game"].debug_log.add(mgs0)

        e_id: int
        for e_id in self.act_on(["velo", "pos"]):

            ent: dict[str, Any]
            ent = self.entities[e_id]

            vy: int
            vx: int
            vy, vx = ent["velo"]


            y: int
            x: int
            y, x, map_id = ent["pos"]

            dy: int
            dx: int
            dy, dx = vy + y, vx + x

            name: Optional[str]
            name = ent.get("name")

            if not name:
                name = f"<entity {e_id}>"

            if (dy not in range(self.pool.etc["game"].game_map["map_height"]) or
                dx not in range(self.pool.etc["game"].game_map["map_width"])):
                return

            ent_in: int
            for ent_in in self.entities[map_id]["map_array"][dy][dx]:
                if self.entities[ent_in].get("player"):
                    self.pool.etc["game"].log.append(f"{name} wants some pets")
                    break

                if (self.entities[ent_in].get("blocks_path")
                    and not self.pool.etc["game"].config["debug"]["disable_collision"]
                    and not ent_in == e_id):

                    tile: dict[str, Any] = self.entities[ent_in]
                    tile_name: Optional[str] = tile.get("name")

                    log_role: str = "something"

                    if not tile_name:
                        tile_name = f"<entity {ent_in}>"

                    log = f"{name} bumps into {log_role} ({tile_name})"

                    if (y, x) in self.pool.etc["game"].player["FOV"]:
                        self.pool.etc["game"].log.append(log)
                    break
            else:

                self.entities[e_id]["pos"] = (dy, dx, map_id)
                self.pool.entities[map_id]["map_array"][dy][dx].append(e_id)
                self.pool.entities[map_id]["map_array"][y][x].remove(e_id)

            self.pool.remove_component_from_entity("velo", e_id)
            if ent.get("FOV"):
                self.pool.add_components_to_entity({"update_fov": True}, e_id)
