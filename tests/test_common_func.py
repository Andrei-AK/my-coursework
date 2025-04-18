from freezegun import freeze_time

from src.common_func import welcome_time


@freeze_time("2025-01-01 00:00:00")
def test_welcome_time_evening():
    result = welcome_time()
    assert result == "Добрый вечер!"


@freeze_time("2025-01-01 12:00:00")
def test_welcome_time_noon():
    result = welcome_time()
    assert result == "Добрый день!"


@freeze_time("2025-01-01 8:00:00")
def test_welcome_time_morning():
    result = welcome_time()
    assert result == "Доброе утро!"


@freeze_time("2025-01-01 1:00:00")
def test_welcome_time_night():
    result = welcome_time()
    assert result == "Доброй ночи!"
