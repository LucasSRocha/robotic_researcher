import json
from abc import ABC, abstractmethod
from csv import DictWriter
from pathlib import Path
from typing import TypeAlias

from RPA.Browser.Selenium import Selenium, selenium_webdriver

WebElement: TypeAlias = selenium_webdriver.remote.webelement.WebElement


class BaseBot(ABC):
    def __init__(
        self,
        bot_name: str,
        browser: Selenium,
        headless=False,
    ) -> None:
        self.bot_name = bot_name
        self.browser = browser
        self.browser.set_selenium_implicit_wait(3)
        self.headless = headless

    def say_hello(self) -> None:
        print(f"Hello, my name is {self.bot_name}.\n")

    def say_goodbye(self) -> None:
        print("Goodbye!\n")

    @abstractmethod
    def explain_functionality(self) -> None:
        pass

    def get_browser_name(self) -> str:
        self.open_webpage(url=None, headless=True)
        browser_info = self.browser.get_browser_capabilities()
        browser_name = browser_info["browserName"]
        self.browser.close_browser()
        return browser_name

    def open_webpage(self, url: str | None, *args, **kwargs) -> None:
        kwargs["headless"] = kwargs.get("headless", self.headless)
        self.browser.open_available_browser(url, *args, **kwargs)

    def input_text(self, input_path: str | WebElement, input_text: str | int | float, clear=True) -> None:
        self.browser.input_text(locator=input_path, text=input_text, clear=clear)

    def get_browser_current_url(self) -> str:
        return self.browser.driver.current_url

    def _write_file(self, filename: str, data: any, suffix: str) -> None:
        file = Path(filename)
        if not file.suffix:
            file = Path(f"{filename}.{suffix}")

        if suffix == "json":
            data = json.dumps(data)
        elif suffix == "txt":
            data = "\n".join([self.compose_scientist_info(**info) for info in data])
        file.write_text(data)

    def _write_csv(self, filename: str, data: list[dict], suffix: str) -> None:
        file = Path(filename)
        if not file.suffix:
            file = Path(f"{filename}.{suffix}")
        with open(file, "w") as f:
            writer = DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
