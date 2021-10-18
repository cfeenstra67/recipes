
check:
	poetry run pylint scraping

fmt:
	poetry run black scraping
