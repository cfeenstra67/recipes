
check:
	poetry run black --check recipes __main__.py
	poetry run pylint recipes

fmt:
	poetry run black recipes __main__.py

deploy-shub:
	poetry export -f requirements.txt --output requirements.txt
	poetry run shub deploy


docker-build:
	docker buildx build  --platform linux/amd64 -t recipes:latest --load 

docker-push: REPO_URL = $(shell pulumi stack output repo_url)
docker-push:
	docker tag recipes:latest $(REPO_URL):latest
	docker push $(REPO_URL):latest

up:
	poetry run pulumi up
