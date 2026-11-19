from cursed_descent.controller import GameController
from cursed_descent.family_tree import family_tree
from cursed_descent.town_buildings.family import link


def test_tree_lists_parents_partner_siblings_and_children(
        controller:GameController) -> None:
    repository = controller.repository
    kerl = repository.load("kerl")
    hero = repository.load("galactica")
    link(kerl, hero, "mother")
    kerl.offspring.append({"name": "Pip", "kind": "party", "species": "human",
                           "surname": "Kerl", "runs": 3})
    kerl.profile["grown_up"] = [{"name": "Old Grubb", "species": "ogre"}]
    rows = family_tree(kerl, repository)
    texts = [text for _, text in rows]
    assert any(text.startswith("Mother: ") for text in texts)
    assert any("you" in text for text in texts)
    assert any("Pip Kerl (human, 3/20 runs)" in text for text in texts)
    assert "Grown up: Old Grubb (ogre)" in texts
    levels = dict((text, level) for level, text in rows)
    assert levels[next(t for t in texts if t.startswith("Mother"))] == 1


def test_the_other_parent_sees_the_child_in_the_tree(
        controller:GameController) -> None:
    repository = controller.repository
    kerl = repository.load("kerl")
    hero = repository.load("galactica")
    kerl.offspring.append({"name": "Pip", "kind": "party", "species": "human",
                           "surname": "Kerl", "runs": 1,
                           "parent": hero.name, "parent_id": hero.id})
    repository.save(kerl)
    texts = [text for _, text in family_tree(hero, repository)]
    assert any("Pip" in text and "carried by" in text for text in texts)
    own = [text for _, text in family_tree(kerl, repository)]
    assert any("with " + hero.name in text for text in own)
