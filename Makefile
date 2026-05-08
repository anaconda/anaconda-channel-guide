.ONESHELL:
SHELL := /bin/bash
.SHELLFLAGS := -c -o pipefail -o errexit
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: clean env test help
.DEFAULT_GOAL := help

CONDA_ENV_NAME ?= anaconda-channel-guide

help:            ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

env:     ## Create conda environment and install package
	conda env create -f environment.yml --name $(CONDA_ENV_NAME) --yes
	conda run --name $(CONDA_ENV_NAME) pip install -e .

test:            ## Run tests
	$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && python -m pytest -vv tests/

clean:           ## Remove conda environment
	conda remove -y -n $(CONDA_ENV_NAME) --all