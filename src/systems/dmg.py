#!/usr/bin/env python3

import ecs

class DmgSystem(ecs.System):

    def update(self):

        for entity_id in self.act_on(["health", "dmg"]):

            ent = self.pool.entities[entity_id]
            max_hp = ent["health"]["max_hp"]
            current_hp = ent["health"]["current_hp"]
            dmg = ent["dmg"]["amount"]

            self.pool.etc["game"].log.append(f"{ent['name']} took {dmg} dmg!")
            if current_hp - dmg > 0:
                ent["health"]["current_hp"] = current_hp - dmg
                self.pool.remove_component_from_entity("dmg", entity_id)
            else:
                self.pool.add_components_to_entity({"died": True}, entity_id)
