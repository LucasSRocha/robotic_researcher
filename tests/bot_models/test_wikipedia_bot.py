from datetime import datetime

import pytest
from RPA.Browser.Selenium import Selenium

from bot_models.wikipedia_bot import ElementNotFound, WikipediaBot


@pytest.fixture
def mock_wikipedia_bot(mocker) -> WikipediaBot:
    return WikipediaBot(bot_name="testerson", browser=mocker.MagicMock())


def test_calculate_age(mock_wikipedia_bot) -> None:
    birth_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
    death_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    age = mock_wikipedia_bot.calculate_age(birth_date, death_date)
    assert age == 20


def test_calculate_age_no_death_date(mock_wikipedia_bot) -> None:
    birth_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
    age = mock_wikipedia_bot.calculate_age(birth_date, None)
    assert age == datetime.now().year - birth_date.year


def test_format_scientist_info(mock_wikipedia_bot, capfd) -> None:
    scientist_info = {
        "scientist_name": "test",
        "first_paragraph": "Test paragraph.",
        "birth_date": datetime.strptime("2000-01-01", "%Y-%m-%d"),
        "death_date": datetime.strptime("2020-01-01", "%Y-%m-%d"),
        "age": 20,
    }
    resp = mock_wikipedia_bot.compose_scientist_info(**scientist_info)
    expected_output = (
        "Test\n"
        "Birth date: 01 January 2000\n"
        "Death date: 01 January 2020\n"
        "Age: 20\n"
        "First Paragraph: Test paragraph.\n"
        "\n"
    )
    assert expected_output in resp


@pytest.mark.parametrize(
    "method, exception",
    [("input_text", ElementNotFound), ("wait_and_click_button", AssertionError)],
)
def test_crawl_scientist_search_not_working(mock_wikipedia_bot, method, exception, mocker) -> None:
    setattr(mock_wikipedia_bot.browser, method, mocker.MagicMock(side_effect=exception))
    response = mock_wikipedia_bot.crawl_scientist("Albert Einstein")
    assert response["found"] is False
    assert response["scientist_name"] == "Albert Einstein"
    assert "Search bar or button not found, possible layout problem" in response["exceptions"]


def test_crawl_scientist_not_found(mock_wikipedia_bot) -> None:
    mock_wikipedia_bot.browser.driver.current_url = "google.com"
    response = mock_wikipedia_bot.crawl_scientist("Albert Einstein")
    assert response["found"] is False
    assert response["scientist_name"] == "Albert Einstein"
    assert "Scientist not found" in response["exceptions"]


def test_crawl_scientist_paragraph_not_found(mock_wikipedia_bot, mocker) -> None:
    mock_wikipedia_bot.browser.get_text = mocker.MagicMock(side_effect=ElementNotFound)
    mock_wikipedia_bot.browser.driver.current_url = "https://en.wikipedia.org/wiki/Albert_Einstein"

    response = mock_wikipedia_bot.crawl_scientist("Albert Einstein")
    assert response["found"] is True
    assert response["scientist_name"] == "Albert Einstein"
    assert "First paragraph not found, check xpath locator and layout" in response["exceptions"]


def test_crawl_scientist_found(mock_wikipedia_bot, mocker) -> None:
    death_date = datetime(year=1955, month=4, day=18)
    mock_death_date = mocker.MagicMock()
    mock_death_date.get_attribute.return_value = death_date.strftime("%Y-%m-%d")

    birth_date = datetime(year=1879, month=3, day=14)
    mock_birth_date = mocker.MagicMock()
    mock_birth_date.get_attribute.return_value = birth_date.strftime("%Y-%m-%d")

    mock_wikipedia_bot.browser.driver.current_url = "https://en.wikipedia.org/wiki/Albert_Einstein"
    mock_wikipedia_bot.browser.get_text.return_value = "Albert Einstein was a theoretical physicist..."
    mock_wikipedia_bot.browser.find_elements = mocker.MagicMock(side_effect=[[mock_death_date], [mock_birth_date]])

    response = mock_wikipedia_bot.crawl_scientist("Albert Einstein")

    assert response["found"] is True
    assert response["scientist_name"] == "Albert Einstein"
    assert response["first_paragraph"] == "Albert Einstein was a theoretical physicist..."
    assert response["birth_date"] == birth_date
    assert response["death_date"] == death_date
    assert response["age"] == 76


def test_run(mock_wikipedia_bot, mocker) -> None:
    scientist_info = {
        "found": True,
        "scientist_name": "Testerson",
        "first_paragraph": "This is a test paragraph",
        "birth_date": datetime(year=1879, month=3, day=14),
        "death_date": datetime(year=1955, month=4, day=18),
        "age": 76,
        "exceptions": [],
    }
    mocker.patch.object(mock_wikipedia_bot, "crawl_scientist")
    mock_wikipedia_bot.crawl_scientist.return_value = scientist_info
    mock_wikipedia_bot.run({"Testerson"})


@pytest.mark.integration
def test_crawl_scientist() -> None:
    bot = WikipediaBot(bot_name="test_bot", browser=Selenium(), headless=True)
    response = bot.crawl_scientist("Albert Einstein")

    assert response["birth_date"] == datetime(year=1879, month=3, day=14)
    assert response["death_date"] == datetime(year=1955, month=4, day=18)
    assert response["age"] == 76
    assert (
        response["first_paragraph"]
        == """Albert Einstein (/ˈaɪnstaɪn/ EYEN-styne;[4] German: [ˈalbɛʁt ˈʔaɪnʃtaɪn] (listen); 14 March 1879 – 18 April 1955) was a German-born theoretical physicist,[5] widely acknowledged to be one of the greatest and most influential physicists of all time. Best known for developing the theory of relativity, he also made important contributions to the development of the theory of quantum mechanics. Relativity and quantum mechanics are the two pillars of modern physics.[1][6] His mass–energy equivalence formula E = mc2, which arises from relativity theory, has been dubbed "the world\'s most famous equation".[7] His work is also known for its influence on the philosophy of science.[8][9] He received the 1921 Nobel Prize in Physics "for his services to theoretical physics, and especially for his discovery of the law of the photoelectric effect",[10] a pivotal step in the development of quantum theory. His intellectual achievements and originality resulted in "Einstein" becoming synonymous with "genius".[11] Einsteinium, one of the synthetic elements in the periodic table, was named in his honor.[12]"""
    )
