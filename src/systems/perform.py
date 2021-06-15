import ecs


class Perform(ecs.System):

    def update(self):

        for entity_id in self.act_on(["Perform"]):
            entity = self.entities[entity_id]
            current_round, goal_round = entity["Perform"]["round"]
            components = entity["Perform"]["components"]
            entity["Perform"]["round"] = (current_round + 1, goal_round)
            if current_round + 1 >= goal_round:
                self.pool.add_components_to_entity(components, entity_id)
                self.pool.remove_component_from_entity("Perform", entity_id)
