from datetime import datetime
from math import floor
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase
from typing import Dict, List, Set

from dateparser import parse as date_parse
from RPA.Browser.Selenium import ElementNotFound

from bot_models.base_bot import BaseBot, WebElement
from utils.string_utils import clean_string_with_extra_spaces


class WikipediaBot(BaseBot):
    base_url = "https://en.wikipedia.org/"
    # notice the "en" fixing the language to avoid void references in the page by mixing languages

    @staticmethod
    def explain_functionality(scientist_name: str, browser_name: str) -> None:
        print(
            f"To obtain the information about {scientist_name} I'll open an available web browser and search wikipedia for you.\n"
            f"After that I'll output here the birthdate, the deathdate (if the scientist is dead), their age and the first paragraph that exists at wikipedia.\n"
            "The steps are:\n"
            f"1. Open the {browser_name} browser and Navigate to Wikipedia.\n"
            f"2. Search for {scientist_name}.\n"
            f"3. In the {scientist_name} page, I'll look for the information required (i.e. birth date, death date,...).\n"
            "4. Close the browser.\n"
            "5. Output the collected information for you in this terminal.\n\n"
        )

    @staticmethod
    def calculate_age(birth_date: datetime, death_date: datetime | None) -> int | str:
        death_date = death_date or datetime.now()
        age_delta = death_date - birth_date
        return floor(age_delta.days / 365)

    @staticmethod
    def url_contain_scientist_name(scientist_name: str, url: str) -> bool:
        clean_name = clean_string_with_extra_spaces(string=scientist_name)
        return any(name_el.lower() in url.lower() for name_el in clean_name.split(" "))

    @staticmethod
    def extract_datetime_from_elements(
        elements: List[WebElement | None],
    ) -> datetime | None:
        if not elements:
            return None
        parsed_dates = [date_parse(el.get_attribute("textContent")) for el in elements]
        return parsed_dates[0] if parsed_dates else None

    @staticmethod
    def get_biography_row_span_xpath(row_identifier: str) -> str:
        """
        returns the xpath that retrieves all span tags for the biography sidecar using a text identifier, such as Born, Died, Citizenship, ...
        it uses normalize-space to remove any trailing or loose spaces and translate to normalize the case of the identifying text.
        """
        return (
            f'//table[@class="infobox biography vcard"]'
            f"/tbody/tr"
            f'/th[translate(normalize-space(text()), "{ascii_uppercase}", "{ascii_lowercase}")="{row_identifier.lower()}"]/..//span'
        )

    def search_scientist(self, scientist_name: str) -> None:
        try:
            self.input_text("//input[@id='searchInput']", scientist_name)
            self.browser.wait_and_click_button("//button[text()='Search']")
        except (ElementNotFound, AssertionError):
            raise Exception("Search bar or button not found, possible layout problem")

    def extract_date(self, identifier: str) -> datetime | None:
        elements = self.browser.find_elements(self.get_biography_row_span_xpath(row_identifier=identifier))
        return self.extract_datetime_from_elements(elements=elements)

    def crawl_scientist(self, scientist_name: str) -> Dict[str, str | datetime | int | None | List[str]]:
        self.open_webpage(self.base_url)
        response = {
            "found": False,
            "age": None,
            "birth_date": None,
            "death_date": None,
            "first_paragraph": None,
            "scientist_name": scientist_name,
            "exceptions": [],
        }

        try:
            self.search_scientist(scientist_name)
        except Exception as e:
            response["exceptions"].append(str(e))
            return response

        if not self.url_contain_scientist_name(scientist_name=scientist_name, url=self.get_browser_current_url()):
            response["exceptions"].append("Scientist not found")
            return response

        response["found"] = True

        try:
            response["first_paragraph"] = self.browser.get_text(
                "//div[@class='mw-parser-output']/p[not(@class='mw-empty-elt')][1]"
            )
        except ElementNotFound:
            response["exceptions"].append("First paragraph not found, check xpath locator and layout")

        death_date = self.extract_date("died")
        if death_date:
            response["death_date"] = death_date

        birth_date = self.extract_date("born")
        if birth_date:
            response["birth_date"] = birth_date
            response["age"] = self.calculate_age(birth_date=birth_date, death_date=death_date)

        self.browser.close_browser()
        return response

    def compose_scientist_info(
        self,
        scientist_name: str,
        first_paragraph: str | None,
        birth_date: datetime | None,
        death_date: datetime | None,
        age: int | None,
        **_,
    ) -> str:
        info_not_found = "Information not found"

        if death_date is None and isinstance(birth_date, datetime):
            death_date = f"Still Alive as of {datetime.now().strftime('%B %Y')}"
        elif isinstance(death_date, datetime):
            death_date = f"Death date: {death_date.strftime('%d %B %Y')}"
        else:
            death_date = "Death date: Information not found"

        info = [
            scientist_name.title(),
            f"Birth date: {birth_date.strftime('%d %B %Y') if birth_date is not None else info_not_found}",
            death_date,
            f"Age: {age if age is not None else info_not_found}",
            f"First Paragraph: {first_paragraph if first_paragraph is not None else info_not_found}",
            "\n",
        ]
        return "\n".join(info)

    def handle_output(self, silent: bool, output_file: str | None, people_info: list[dict], output_format: str) -> None:
        output_functions = {"csv": self._write_csv, "txt": self._write_file, "json": self._write_file}
        if not silent:
            [print(self.compose_scientist_info(**info)) for info in people_info]

        if output_file:
            output_file = Path(output_file)
            if not output_file.suffix or output_file.suffix != output_format:
                output_file = Path(f"{output_file}.{output_format}")

            counter = 0
            original_output_path = Path(output_file)

            while Path(output_file).exists():
                base = original_output_path.stem
                ext = original_output_path.suffix
                counter += 1
                output_file = f"{base}_{counter}{ext}"

            output_functions[output_format](filename=output_file, data=people_info, suffix=output_format)

    def run(self, scientists: Set[str], silent=False, output_file: str | None = None, output_format: str = "") -> None:
        if not silent:
            self.say_hello()

        people_info = []
        for scientist_name in scientists:
            if not silent:
                self.explain_functionality(scientist_name=scientist_name, browser_name=self.get_browser_name())

            people_info.append(self.crawl_scientist(scientist_name=scientist_name))

        self.handle_output(
            silent=silent,
            output_file=output_file,
            people_info=people_info,
            output_format=output_format,
        )

        if not silent:
            self.say_goodbye()
