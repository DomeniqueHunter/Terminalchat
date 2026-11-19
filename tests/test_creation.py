from cursed_descent.config import START_FREE_POINTS, START_STAT_VALUE
from cursed_descent.creation import (
    CharacterCreator, find_gender, parse_distribution,
)
from cursed_descent.storage import PlayerRepository


def test_find_gender_by_number_and_name() -> None:
    assert find_gender("1") == find_gender(" male ")
    assert find_gender("99") is None
    assert find_gender("nonsense") is None


def test_parse_distribution_accepts_exact_sum() -> None:
    result = parse_distribution("4 2 2 2")
    assert result == {"strength": 4, "agility": 2, "vitality": 2,
                      "intelligence": 2}


def test_parse_distribution_rejects_bad_input() -> None:
    assert isinstance(parse_distribution("1 2 3"), str)
    assert isinstance(parse_distribution("a b c d"), str)
    assert isinstance(parse_distribution("1 1 1 1"), str)


def test_full_creation_flow(repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    assert creator.is_active("Lyra")
    creator.answer("Lyra", "Lyra Dawn")
    creator.answer("Lyra", "female")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "rest")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "4 2 2 2")
    messages, player = creator.answer("Lyra", "yes")
    assert messages == []
    assert player.gender == find_gender("female")
    assert (player.first_name, player.last_name) == ("Lyra", "Dawn")
    assert player.full_name == "Lyra Dawn"
    assert player.id
    assert player.stats["strength"] == START_STAT_VALUE + 4
    assert sum(player.stats.values()) == 4 * START_STAT_VALUE + (
        START_FREE_POINTS)
    assert repository.exists("Lyra")
    assert not creator.is_active("Lyra")


def test_unknown_gender_repeats_question(
        repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    creator.answer("Lyra", "ok")
    messages, player = creator.answer("Lyra", "banana")
    assert player is None
    assert "I don't know" in messages[0].text


def test_cancel_aborts_creation(repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    messages, player = creator.answer("Lyra", "cancel")
    assert player is None and not creator.is_active("Lyra")
    assert not repository.exists("Lyra")


def test_declining_summary_restarts(repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "1")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "rest")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "4 2 2 2")
    messages, player = creator.answer("Lyra", "no")
    assert player is None and creator.is_active("Lyra")
    assert "starting over" in messages[0].text
    assert "Step 1/6" in messages[0].text


def test_one_word_name_and_ok_keep_handle(
        repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "1")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "rest")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "4 2 2 2")
    _, player = creator.answer("Lyra", "yes")
    assert (player.first_name, player.last_name) == ("Lyra", "")
    assert player.full_name == "Lyra"


def test_too_many_name_words_are_rejected(
        repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    messages, _ = creator.answer("Lyra", "a b c")
    assert "one or two words" in messages[0].text


def test_recreated_character_can_reuse_an_id(
        repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra", char_id="abc123")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "1")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "rest")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "4 2 2 2")
    _, player = creator.answer("Lyra", "yes")
    assert player.id == "abc123"


def start_at_body(repository:PlayerRepository,
                  gender:str="female") -> CharacterCreator:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", gender)
    creator.answer("Lyra", "ok")
    return creator


def test_body_is_asked_question_by_question(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    messages, _ = creator.answer("Lyra", "ok")
    assert "question 2 of 7" in messages[0].text
    messages, _ = creator.answer("Lyra", "back")
    assert "question 1 of 7" in messages[0].text
    assert "allowed at start" in messages[0].text


def test_hung_characters_get_the_extra_questions(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository, "male")
    messages, _ = creator.answer("Lyra", "back")
    assert "of 11" in messages[0].text


def test_out_of_range_value_repeats_the_same_question(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    messages, _ = creator.answer("Lyra", "5")
    text = messages[0].text
    assert "outside the start range" in text and "question 1 of 7" in text


def test_stat_numbers_at_the_body_step_do_not_advance(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    messages, _ = creator.answer("Lyra", "5 1 4 0")
    assert "Step 4/6" in messages[0].text
    assert "stat points" in messages[0].text


def test_all_errors_are_listed_at_once(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository, "male")
    messages, _ = creator.answer(
        "Lyra", "bust 1300 muscle 100 butt 130 girth 35 balls 45")
    text = messages[0].text
    assert "Bust size" in text and "Ball diameter" in text
    assert "Cock girth" in text


def test_pairs_lead_to_the_review_step(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    messages, _ = creator.answer("Lyra", "height 180 bust 400")
    assert "review" in messages[0].text and "180 cm" in messages[0].text
    messages, _ = creator.answer("Lyra", "ok")
    assert "Step 5/6" in messages[0].text


def test_choice_questions_accept_numbers(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    creator.answer("Lyra", "ok")
    creator.answer("Lyra", "ok")
    messages, _ = creator.answer("Lyra", "4")
    assert "question 4 of 7" in messages[0].text
    assert creator.states["lyra"].body["build"] == "Toned"


def test_bad_stats_repeat_the_stats_question(
        repository:PlayerRepository) -> None:
    creator = start_at_body(repository)
    creator.answer("Lyra", "rest")
    creator.answer("Lyra", "ok")
    messages, _ = creator.answer("Lyra", "1 1 1 1")
    assert "has to be exactly" in messages[0].text
    assert "Step 5/6" in messages[0].text


def test_race_is_chosen_after_gender_and_fits_the_body(
        repository:PlayerRepository) -> None:
    creator = CharacterCreator(repository)
    creator.start("Lyra")
    creator.answer("Lyra", "Lyra Dawn")
    messages, _ = creator.answer("Lyra", "female")
    assert "Step 3/6" in messages[0].text and "Human" in messages[0].text
    assert "Goblin" not in messages[0].text
    for refused in ("elf", "dwarf", "goblin", "vampire"):
        messages, _ = creator.answer("Lyra", refused)
        assert "I don't know" in messages[0].text
    messages, _ = creator.answer("Lyra", "human")
    assert "Step 4/6" in messages[0].text and "175" in messages[0].text
    creator.answer("Lyra", "height 210 weight 150")
    creator.answer("Lyra", "rest")
    messages, _ = creator.answer("Lyra", "ok")
    assert "adjusted to fit the race" in messages[0].text
    creator.answer("Lyra", "4 2 2 2")
    _, player = creator.answer("Lyra", "yes")
    assert player.race == "human"
    assert player.body["height"] <= 200 and player.body["weight"] <= 160
