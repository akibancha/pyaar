from __future__ import annotations
from typing import Any, Optional, List


class System:

    def __init__(self,
                 name: str,
                 pool: Pool):
        self.name: str = name
        self.active: bool = True
        self.pool: Pool = pool
        self.entities: dict = self.pool.entities
        self.components: dict = self.pool.components

    def update(self):
        pass

    def act_on(self,
               components: List[str]) -> set:
        inside = list()
        outside = list()
        for component in components:
            if self.components.get(component):
                if component[0] == "!":
                    outside.append(self.components[component[1:]])
                else:
                    inside.append(self.components[component])
            else:
                return set()

        return set.intersection(*inside).difference(*outside)


def test_param_for_type(test: Any, should_be: Any, name: str):
    """
    Tests if a given parameter is of the right type.
    :param test: Any - The parameter you want to test
    :param should_be: Any - The type the parameter should have
    :param name: str - The name of the parameter
    :return:
    """
    err_msg = f"The given {name}: {test} is type: {type(test)}\
        , but needs to be {should_be}!"
    assert isinstance(test, should_be), err_msg


class Pool:

    """
    Container Class for entities, components and systems
    """

    def __init__(self,
                 name: str) -> None:
        self.name = name
        self.entities = dict()
        self.components = dict()
        self.systems = dict()
        self.system_layers = dict()
        self.entity_id = 0
        self.dead_entity_ids = set()
        self.etc = dict()

    def clean_entities(self) -> None:
        """
        Removes all entities from the pool.
        :return: None
        """
        for key in self.components:
            self.components[key] = set()
        self.entities = dict()

    def clean_components(self) -> None:
        """
        Removes all components from the pool.
        This will most likely break the whole pool. Don't do this, it makes
        small bunnies cry and nobody likes people who make small bunnies cry.
        :return: None
        """
        self.components = dict()

    def clean_systems(self) -> None:
        """
        Removes all Systems from the pool.
        :return: None
        """
        self.systems = dict()
        self.system_layers = dict()

    def add_entity(self,
                   blueprint: dict) -> int:

        """
        Adds a new entity to the pool.

        :param blueprint: dict
               (example:
                blueprint = {"component1": some data,
                             "component2": some data,
                             ...,
                             ...})
        :return: int - the entity id of the added entity
        """

        test_param_for_type(blueprint, dict, "blueprint")

        if self.dead_entity_ids:
            entity_id = self.dead_entity_ids.pop()
        else:
            entity_id = self.entity_id
            self.entity_id += 1
        self.entities[entity_id] = dict()
        self.add_components_to_entity(blueprint, entity_id)
        return entity_id

    def remove_entity(self,
                      entity_id: int) -> None:
        """
        Removes an entity from the pool.
        :param entity_id: int - the entity id you want to remove.
        :return: None
        """

        test_param_for_type(entity_id, int, "entity id")
        for key in self.entities[entity_id].keys():
            self.components[key].remove(entity_id)
        del self.entities[entity_id]
        self.dead_entity_ids.add(entity_id)

    def add_system(self,
                   system: Any,
                   name: str,
                   layer: int,
                   active: Optional[bool] = True) -> None:
        """
        Adds a system to the pool.

        :param system: System - The system you want to add to the pool.
        :param name:  str - The name of the system.
        :param layer: int - The system execution layer.
        (determinates the order in which the systems will be updated)
        :param active: Optional[bool]=True - The activation state of the system
        (determinates if the system will be updated during
        the next pool update)
        :return: None
        """

        test_param_for_type(name, str, "system name")
        test_param_for_type(layer, int, "system layer")
        if active is not True:
            test_param_for_type(active, bool, "active state")
        if not self.system_layers.get(layer):
            self.system_layers[layer] = list()
        self.system_layers[layer].append(name)
        self.systems[name] = system(name=name, pool=self)

    def add_component_to_pool(self,
                              component: str) -> None:
        if not self.components.get(component):
            self.components[component] = set()

    def remove_component_from_pool(self,
                                   component: str) -> None:
        for entity in self.components[component]:
            del self.entities[entity][component]
        del self.components[component]

    def remove_component_from_entity(self,
                                     component: str,
                                     entity_id: int) -> None:
        del self.entities[entity_id][component]
        self.components[component].remove(entity_id)

    def add_components_to_entity(self,
                                 components: dict,
                                 entity_id: int) -> None:
        for key, item in components.items():
            if key not in self.components:
                self.add_component_to_pool(key)
            if entity_id not in self.components[key]:
                self.components[key].add(entity_id)
            if key not in self.entities[entity_id]:
                self.entities[entity_id][key] = item

    def set_system_activity(self,
                            system: str,
                            active: bool) -> None:
        self.systems[system].active = active

    def get_system_status(self,
                          system: str) -> bool:
        return self.systems[system].active

    def update(self,
               systems: Optional[List[str]] = None,
               layers: Optional[List[int]] = None):

        if systems and not layers:
            for system in systems:
                self.systems[system].update()
                return
        if layers and not systems:
            for layer in sorted(layers):
                for system in self.system_layers[layer]:
                    self.systems[system].update()

        if not systems and not layers:
            for layer in sorted(self.system_layers.keys()):
                for system in self.system_layers[layer]:
                    self.systems[system].update()
