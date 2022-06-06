POETRY=poetry
POETRY_RUN=$(POETRY) run

SOURCE_FILES=$(shell find . -name '*.py' -not -path **/.venv/*)
SOURCES_FOLDER=medium_collector
DATE=$(shell date "+%d %B of %Y at %H:%M")

download:
	$(POETRY_RUN) python -m medium_collector from-mail

version:
	$(POETRY_RUN) kaggle datasets version -p data -m "Data update $(DATE)"

format:
	$(POETRY_RUN) isort -rc $(SOURCES_FOLDER)
	$(POETRY_RUN) black $(SOURCE_FILES)

lint:
	$(POETRY_RUN) isort -rc $(SOURCES_FOLDER) --check-only
	$(POETRY_RUN) black $(SOURCE_FILES) --check
	$(POETRY_RUN) pylint $(SOURCES_FOLDER)
