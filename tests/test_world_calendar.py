from cursed_descent.town_buildings.world_days import calendar, date_text


def test_calendar_starts_on_monday_day_one() -> None:
    assert calendar(0) == (1, 1, "Monday")
    assert date_text(6) == "Sunday, day 7 of year 1"


def test_year_rolls_over_after_365_days() -> None:
    assert calendar(364) == (1, 365, "Monday")
    year, in_year, weekday = calendar(365)
    assert (year, in_year, weekday) == (2, 1, "Tuesday")
