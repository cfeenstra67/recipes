import logging
from datetime import datetime
from typing import Iterator, Any

import scrapy
from recipe_scrapers import scrape_me

from recipes import site_listers, items


LOGGER = logging.getLogger(__name__)


class RecipeSpider(scrapy.Spider):
    """
    Spider for scraping recipe data
    """

    name = "recipes"

    recipe_generators = [
        site_listers.ACoupleCooksLister(),
        site_listers.AllRecipesLister(),
        site_listers.AmbitiousKitchenLister(),
        site_listers.ArchanasKitchenLister(),
        site_listers.AverieCooksLister(),
        site_listers.BakingSenseLister(),
        site_listers.BakingMischiefLister(),
        site_listers.BBCLister(),
        site_listers.BBCGoodFoodLister(),
        site_listers.BettyCrockerLister(),
        site_listers.BonAppetitLister(),
        site_listers.BowlOfDeliciousLister(),
        site_listers.BudgetBytesLister(),
        site_listers.CastIronKetoLister(),
        site_listers.ClosetCookingLister(),
        site_listers.CookEatShareLister(),
        site_listers.CookieAndKateLister(),
        site_listers.CookStrLister(),
        site_listers.EatingBirdFoodLister(),
        site_listers.EatSmarterLister(),
        site_listers.EatWhatTonightLister(),
        site_listers.EpicuriousLister(),
        site_listers.FoodLister(),
        site_listers.FoodNetworkLister(),
        site_listers.FoodRepublicLister(),
        site_listers.ForksOverKnivesLister(),
        site_listers.GimmeSomeOvenLister(),
        site_listers.GonnaWantSecondsLister(),
        site_listers.GreatBritishChefsLister(),
        site_listers.HalfBakedHarvestLister(),
        site_listers.HeadBangersKitchenLister(),
        site_listers.HelloFreshLister(),
        site_listers.HostTheToastLister(),
        site_listers.IndianHealthyRecipesLister(),
        site_listers.InnitLister(),
        site_listers.JamieOliverLister(),
        site_listers.JimCooksGoodFoodLister(),
        site_listers.JoyFoodSunshineLister(),
        site_listers.JustATasteLister(),
        site_listers.JustBentoLister(),
        site_listers.KennyMcgovernLister(),
        site_listers.KingArthurBakingLister(),
        site_listers.LeCremeDeLaCrumbLister(),
        site_listers.LittleSpiceJarLister(),
        site_listers.LivelyTableLister(),
        site_listers.LovingItVeganLister(),
        site_listers.MarthaStewartLister(),
        site_listers.MelsKitchenCafeLister(),
        site_listers.MinimalistBakerLister(),
        site_listers.MomsWithCrockpotsLister(),
        site_listers.MyBakingAddictionLister(),
        site_listers.MyRecipesLister(),
        site_listers.NourishedByNutritionLister(),
        site_listers.NutritionByNathalieLister(),
        site_listers._101CookbooksLister(),
        site_listers.PaleoRunningMommaLister(),
        site_listers.PaniniHappyLister(),
        site_listers.PracticalSelfRelianceLister(),
        site_listers.PrimalEdgeHealthLister(),
        site_listers.PurelyPopeLister(),
        site_listers.PurpleCarrotLister(),
        site_listers.RachlmansFieldLister(),
        site_listers.RainbowPlantLifeLister(),
        site_listers.RealSimpleLister(),
        site_listers.RecipeTinEatsLister(),
        site_listers.RedHouseSpiceLister(),
        site_listers.SallysBakingAddictionLister(),
        site_listers.SaveurLister(),
        site_listers.SeriousEatsLister(),
        site_listers.SimplyQuinoaLister(),
        site_listers.SimplyRecipesLister(),
        site_listers.SimplyWhiskedLister(),
        site_listers.SkinnyTasteLister(),
        site_listers.SouthernLivingLister(),
        site_listers.SpendWithPenniesLister(),
        site_listers.SteamyKitchenLister(),
        site_listers.SunBasketLister(),
        site_listers.SweetCsDesignsLister(),
        site_listers.SweetPeasAndSaffronLister(),
        site_listers.TasteOfHomeLister(),
        site_listers.TastesOfLizzyTLister(),
        site_listers.TastyKitchenLister(),
        site_listers.TheCleverCarrotLister(),
        site_listers.TheHappyFoodieLister(),
        site_listers.TheKitchenMagpieLister(),
        site_listers.TheKitchnLister(),
        site_listers.TheNutritiousKitchenLister(),
        site_listers.TheSpruceEatsLister(),
        site_listers.TheVintageMixerLister(),
        site_listers.TheWoksOfLifeLister(),
        site_listers.TwoPeasAndTheirPodLister(),
        site_listers.VanillaAndBeanLister(),
        site_listers.VegRecipesOfIndiaLister(),
        site_listers.WatchWhatUEatLister(),
        site_listers.WhatsGabyCookingLister(),
        site_listers.WholeFoodsMarketLister(),
        site_listers.WikibooksLister(),
    ]

    def start_requests(self) -> Iterator[Any]:
        # TODO(cam): iterate through these "horizontally" so each generator
        # yields one request at once, should help slightly to distribute
        # requests
        for generator in self.recipe_generators:
            yield from generator.start_requests(self.parse)

    def parse(self, response: scrapy.http.Response) -> Iterator[Any]:

        try:
            scraper = scrape_me(response.url, page_data=response.body)
        except Exception:
            LOGGER.exception("Error creating scraper for %s", response.url)
            return

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
            if not item_dict[field]:
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
