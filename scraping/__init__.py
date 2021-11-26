import os

from scraping.recipe_scrapers_patch import patch_scrapers

patch_scrapers()

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(PROJECT_DIR, "data")
