from argparse import ArgumentParser

from RPA.Browser.Selenium import Selenium

from bot_models.wikipedia_bot import WikipediaBot
from utils.string_utils import clean_string_with_extra_spaces


def main() -> None:
    parser = ArgumentParser(description="Retrieve information about scientists from Wikipedia.")
    parser.add_argument(
        "scientists",
        help="The scientists to search for separated by comma ',' i.e. 'Albert Einstin, Isaac Newton, Marie Curie'.",
    )
    parser.add_argument(
        "-H",
        "--headless",
        action="store_true",
        help="Run the browser in headless mode.",
    )
    parser.add_argument(
        "-S",
        "--silent",
        action="store_true",
        help="Run bot in silent mode (no terminal output).",
    )
    parser.add_argument("-o", "--output_path", help="Path for a file to output the results to.")
    parser.add_argument(
        "-f",
        "--format",
        choices=["txt", "csv", "json"],
        default="csv",
        help="Output format. Can be 'txt','csv' or 'json'. Default is 'csv'.",
    )
    args = parser.parse_args()

    robot = WikipediaBot(
        browser=Selenium(),
        bot_name="Wilson",
        headless=args.headless,
    )
    scientists = {clean_string_with_extra_spaces(i.strip()) for i in args.scientists.split(",")}
    robot.run(scientists=scientists, output_file=args.output_path, silent=args.silent, output_format=args.format)


if __name__ == "__main__":  # pragma: no cover
    main()
