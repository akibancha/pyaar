#!/usr/bin/env python3
import ecs

class DieSystem(ecs.System):

    def update(self):

        for entity_id in self.act_on(["died"]):

            ent = self.entities[entity_id]

            remove_components = [
                "simple_ai",
                "blocks_path",
                "Perform",
                "died",
                "enemy",
                "health",
                "dmg"
            ]

            name = ent.get("name")
            if not name:
                name = f"<entity: {entity_id}>"
                
            self.pool.etc["game"].log.append(f"{name} has died!")
            if ent.get("dead_body"):
                ent["name"] = ent["dead_body"]["name"]
                ent["char"][0][0] = ent["dead_body"]["char"]

            for component in remove_components:
                if ent.get(component):
                    self.pool.remove_component_from_entity(
                        component,
                        entity_id
                    )
            self.pool.add_components_to_entity(
                {"dead": True},
                entity_id
            )
