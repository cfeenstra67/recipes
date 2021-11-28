import inspect
from functools import wraps
from typing import Optional, Tuple, Union

from bs4 import BeautifulSoup
from recipe_scrapers import SCRAPERS
from recipe_scrapers._abstract import AbstractScraper
from recipe_scrapers._schemaorg import SchemaOrg
from recipe_scrapers._utils import normalize_string
from recipe_scrapers.bettycrocker import BettyCrocker
from recipe_scrapers.onehundredonecookbooks import OneHundredOneCookBooks
from recipe_scrapers.recipietineats import RecipieTinEats
from recipe_scrapers.settings import settings


def patch_scrapers() -> None:
    """ """
    patch_abstract_scraper()
    patch_betty_crocker()
    patch_onehundredonecookbooks()
    patch_recipetineats()


def patch_abstract_scraper() -> None:
    """ """
    if not hasattr(AbstractScraper, "__original_init__"):
        AbstractScraper.__original_init__ = AbstractScraper.__init__

    @wraps(AbstractScraper.__original_init__)
    def new_init(  # pylint: disable=too-many-arguments
        self,
        url: str,
        page_data: str,
        proxies: Optional[str] = None,  # pylint: disable=unused-argument
        timeout: Optional[  # pylint: disable=unused-argument
            Union[float, Tuple]
        ] = None,
        wild_mode: Optional[bool] = False,
    ) -> None:

        self.wild_mode = wild_mode
        self.soup = BeautifulSoup(page_data, "lxml")
        self.url = url
        self.schema = SchemaOrg(page_data)

        # attach the plugins as instructed in settings.PLUGINS
        if not hasattr(self.__class__, "plugins_initialized"):
            for name, _ in inspect.getmembers(self, inspect.ismethod):
                current_method = getattr(self.__class__, name)
                for plugin in reversed(settings.PLUGINS):
                    if plugin.should_run(self.host(), name):
                        current_method = plugin.run(current_method)
                setattr(self.__class__, name, current_method)
            setattr(self.__class__, "plugins_initialized", True)

    AbstractScraper.__init__ = new_init


class PatchedBettyCrocker(BettyCrocker):  # pylint: disable=abstract-method
    """ """

    def ingredients(self):
        ingredients = self.soup.find("div", {"class": "rdpIngredients"}).ul.findAll(
            "li"
        )

        return [
            normalize_string(
                ingredient.find("span", {"class": "quantity"}).text
                + " "
                + ingredient.find("span", {"class": "description"}).text
            )
            for ingredient in ingredients
        ]


class PatchedOneHundredOneCookbooks(OneHundredOneCookBooks):
    """
    Failing case: https://www.101cookbooks.com/millionaires-shortbread/
    """
    def title(self):
        title = self.soup.find("h1")
        if title is None:
            title = self.soup.find("h2")
        return title.get_text()


def patch_betty_crocker() -> None:
    """ """
    SCRAPERS[BettyCrocker.host()] = PatchedBettyCrocker


def patch_onehundredonecookbooks() -> None:
    """
    """
    SCRAPERS[OneHundredOneCookBooks.host()] = PatchedOneHundredOneCookbooks


def patch_recipetineats() -> None:
    """
    """
    SCRAPERS["recipetineats.com"] = RecipieTinEats
