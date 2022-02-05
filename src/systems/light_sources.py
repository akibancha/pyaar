import ecs

class LightZones(ecs.System):

    def update(self):

        map_height_range = range(self.pool.etc["game"].game_map["map_height"])
        map_width_range = range(self.pool.etc["game"].game_map["map_width"])
        for id in self.act_on(["update_light_zone", "pos", "last_pos"]):
            ent = self.pool.entities[id]
            light_map = self.pool.etc["game"].game_map["light_map"]
            new_pos_y, new_pos_x, _ = ent["pos"]

            for light in ent["lights"]:
                ly, lx = light
                light_map[ly][lx] = False

            for y in range(
                new_pos_y - ent["light_range"],
                new_pos_y + ent["light_range"] + 1
            ):
                for x in range(
                   new_pos_x - ent["light_range"],
                   new_pos_x + ent["light_range"] + 1 
                ):
                    if y in map_height_range and x in map_width_range:
                        light_map[y][x] = True
                        ent["lights"].append((y, x))

            self.pool.remove_component_from_entity("update_light_zone", id)
