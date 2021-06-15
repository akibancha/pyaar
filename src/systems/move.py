import ecs


class MoveSystem(ecs.System):

    def update(self):

        for e_id in self.act_on(["velo", "pos"]):
            ent = self.entities[e_id]
            vy, vx = ent["velo"]
            y, x, map_id = ent["pos"]
            dy, dx = vy + y, vx + x
            name = ent.get("name")
            if not name:
                name = f"<entity {e_id}>"
            for ent_in in self.entities[map_id]["map_array"][dy][dx]:
                if (self.entities[ent_in].get("unpassable") and not
                    (self.pool.etc["game"].config["debug"]
                                                 ["disable_collision"])):
                    tile = self.entities[ent_in]
                    tile_name = tile.get("name")
                    log_role = "something"
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
