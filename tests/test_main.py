from bot_models.wikipedia_bot import WikipediaBot
from main import main as main_func


def test_main_with_silent_and_headless_options(mocker):
    mock_args = mocker.patch("argparse.ArgumentParser.parse_args")
    mocker.patch("main.Selenium")
    mock_args.return_value = mocker.MagicMock(
        headless=True,
        silent=True,
        scientists="Albert Einstein",
        output_path=None,
        format="txt",
    )

    mock_run = mocker.patch.object(WikipediaBot, "run")
    main_func()
    assert mock_run.called_once
    mock_run.assert_called_once_with(scientists={"Albert Einstein"}, output_file=None, silent=True, output_format="txt")


def test_main_with_output_path(mocker):
    mock_args = mocker.patch("argparse.ArgumentParser.parse_args")
    mocker.patch("main.Selenium")
    mock_args.return_value = mocker.MagicMock(
        headless=False,
        silent=False,
        scientists="Albert Einstein,   Albert   Einstein, Fake  Doctorine   ",
        output_path="/tmp/output.txt",
        format="txt",
    )

    mock_run = mocker.patch.object(WikipediaBot, "run")
    main_func()

    assert mock_run.called_once
    mock_run.assert_called_once_with(
        scientists={"Albert Einstein", "Fake Doctorine"},
        output_file="/tmp/output.txt",
        silent=False,
        output_format="txt",
    )
