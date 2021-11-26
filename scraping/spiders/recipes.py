import logging
from datetime import datetime
from typing import Iterator, Any

import scrapy
from recipe_scrapers import scrape_me

from scraping import site_listers, items


LOGGER = logging.getLogger(__name__)


class RecipeSpider(scrapy.Spider):
    """
    Spider for scraping recipe data
    """

    name = "recipes"

    recipe_generators = [
        # site_listers.ACoupleCooksLister(),
        # site_listers.AllRecipesLister(),
        # site_listers.AmbitiousKitchenLister(),
        # site_listers.ArchanasKitchenLister(),
        # site_listers.AverieCooksLister(),
        # site_listers.BakingSenseLister(),
        # site_listers.BakingMischiefLister(),
        # site_listers.BBCLister(),
        # site_listers.BBCGoodFoodLister(),
        # site_listers.BettyCrockerLister(),
        # site_listers.BonAppetitLister(),
        # site_listers.BowlOfDeliciousLister(),
        # site_listers.BudgetBytesLister(),
        # site_listers.CastIronKetoLister(),
        # site_listers.ClosetCookingLister(),
        # site_listers.CookEatShareLister(),
        # site_listers.CookieAndKateLister(),
        # site_listers.CookStrLister(),
        # site_listers.EatingBirdFoodLister(),
        # site_listers.EatSmarterLister(),
        # site_listers.EatWhatTonightLister(),
        # site_listers.EpicuriousLister(),
        # site_listers.FoodLister(),
        # site_listers.FoodNetworkLister(),
        # site_listers.FoodRepublicLister(),
        # site_listers.ForksOverKnivesLister(),
        # site_listers.GimmeSomeOvenLister(),
        # site_listers.GonnaWantSecondsLister(),
        # site_listers.GreatBritishChefsLister(),
        # site_listers.HalfBakedHarvestLister(),
        # site_listers.HeadBangersKitchenLister(),
        # site_listers.HelloFreshLister(),
        # site_listers.HostTheToastLister(),
        # site_listers.IndianHealthyRecipesLister(),
        # site_listers.InnitLister(),
        # site_listers.JamieOliverLister(),
        # site_listers.JimCooksGoodFoodLister(),
        # site_listers.JoyFoodSunshineLister(),
        # site_listers.JustATasteLister(),
        # site_listers.JustBentoLister(),
        # site_listers.KennyMcgovernLister(),
        # site_listers.KingArthurBakingLister(),
        # site_listers.LeCremeDeLaCrumbLister(),
        # site_listers.LittleSpiceJarLister(),
        # site_listers.LivelyTableLister(),
        # site_listers.LovingItVeganLister(),
        # site_listers.MarthaStewartLister(),
        # site_listers.MelsKitchenCafeLister(),
        # site_listers.MinimalistBakerLister(),
        # site_listers.MomsWithCrockpotsLister(),
        site_listers.MyBakingAddictionLister(),
    ]

    def start_requests(self) -> Iterator[Any]:
        for generator in self.recipe_generators:
            yield from generator.start_requests(self.parse)

    def parse(self, response: scrapy.http.Response) -> Iterator[Any]:
        scraper = scrape_me(response.url, page_data=response.body)

        def get_method_result(func):
            try:
                return True, func()
            except Exception as err:
                return False, err

        fields = {
            "title": get_method_result(scraper.title),
            "total_time": get_method_result(scraper.total_time),
            "yields": get_method_result(scraper.yields),
            "ingredients": get_method_result(scraper.ingredients),
            "instructions": get_method_result(scraper.instructions),
            "image": get_method_result(scraper.image),
            "host": get_method_result(scraper.host),
            "links": get_method_result(scraper.links),
            "nutrients": get_method_result(scraper.nutrients),
        }

        item_dict = {}
        error_count = 0
        field_count = 0

        for key, (is_success, value) in fields.items():
            field_count += 1
            if not is_success:
                error_count += 1
                item_dict[key] = None
                continue
            item_dict[key] = value

        if error_count == field_count:
            LOGGER.error("All fields had errors for %s", response.url)
            return

        for field in ["title", "ingredients", "instructions"]:
            if item_dict[field] is None:
                LOGGER.error("%s does not have a %s", response.url, field)
                return

        item_dict.update(
            {
                "html": response.body,
                "url": response.url,
                "accessed_at": datetime.utcnow().isoformat(),
            }
        )

        yield items.RecipeItem(**item_dict)
