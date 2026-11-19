from cursed_descent.controller import GameController


def test_resolve_accepts_handle_id_and_prefix(
        controller:GameController) -> None:
    repository = controller.repository
    player = repository.load("kerl")
    assert repository.resolve("kerl") == "kerl"
    assert repository.resolve(player.id) == "kerl"
    assert repository.resolve(player.id[:8]) == "kerl"
    assert repository.resolve("nobody") == "nobody"


def test_copies_share_an_id(controller:GameController) -> None:
    repository = controller.repository
    player = repository.load("kerl")
    assert repository.copies_of(player.id) == [player]


def test_controller_accepts_id_as_sender(controller:GameController) -> None:
    char_id = controller.repository.load("kerl").id
    messages = controller.handle(char_id, "!profile")
    assert messages and "kerl" in messages[0].text.lower()
    assert messages[0].recipient == "kerl"
