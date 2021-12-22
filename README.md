# Recipe Scraping

This repository makes use of the [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) Python library to scrape recipes from over 100 websites to build a dataset. Additional projects making use of this dataset may be coming in the future.

The scraper takes the form of a single Scrapy spider, and for deployment it is packaged into a docker image that runs `scrapyd` and allows running and monitoring the spider via API and the web UI respectively.

Also included in this repo is Pulumi code to deploy the docker image to AWS App Runner--this is my first time using this service, but so far my impressions are that it works well (other than the fact that in the case of permission issues it seems to hang for about 30 minutes before failing).

The dataset can be found at `s3://recipe-scraping-b0a81b2/results/*`; it is publicly accessible if you want to access it. You will need to be authenticated to AWS from your account to access it though, and you'll be charged for the data egress if you choose to transfer it out of AWS.
