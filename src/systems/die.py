#!/usr/bin/env python3
import ecs

class DieSystem(ecs.System):

    def update(self):

        for entity_id in self.act_on(["dead"]):

            ent = self.entities[entity_id]

            if ent.get("dead_body"):
                ent["name"] = ent["dead_body"]["name"]
                ent["char"][0][0] = ent["dead_body"]["char"]

            if ent.get("simple_ai"):
                self.pool.remove_component_from_entity("simple_ai", entity_id)

            if ent.get("block_path"):
                self.pool.remove_component_from_entity("blocks_path", entity_id)
