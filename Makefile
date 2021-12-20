
check:
	poetry run black --check scraping
	poetry run pylint scraping

fmt:
	poetry run black scraping

deploy-shub:
	poetry export -f requirements.txt --output requirements.txt
	poetry run shub deploy


docker-build:
	docker build -t recipes:latest .

docker-push: REPO_URL = $(shell pulumi stack output repo_url)
docker-push:
	docker tag recipes:latest $(REPO_URL):latest
	docker push $(REPO_URL):latest

up:
	poetry run pulumi up
