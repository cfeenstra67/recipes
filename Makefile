
check:
	poetry run black --check scraping
	poetry run pylint scraping

fmt:
	poetry run black scraping
