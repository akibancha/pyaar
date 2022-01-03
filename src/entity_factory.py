import random


def create_actor(blueprint: dict) -> dict:

    names = blueprint.get("names")
    attributes = blueprint.get("attributes")
    entity_type = blueprint.get("entity_type")

    hp_range = blueprint.get("hp_range")
    movment_range = blueprint.get("movement_range")

    name_string = []

    if names:
        name_string.append(f"{random.choice(names)}")

    if attributes:
        name_string.append(f"the {random.choice(attributes)}")

    if entity_type:
        name_string.append(f"{entity_type}")

    if hp_range:
        min_hp, max_hp = hp_range
        hp = random.randint(min_hp, min_hp)
        hp_component = {"max_hp": hp,
                        "current_hp": hp}
        blueprint["hp"] = hp_component

    if movment_range:
        min_cost, max_cost = movment_range
        blueprint["movement_cost"] = random.randint(min_cost, max_cost)

    if name_string:
        blueprint["name"] = " ".join(name_string)

    return blueprint
