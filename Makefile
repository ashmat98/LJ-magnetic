hash= $(shell ./utils/md5_hash.py requirements.txt hots-${HOSTNAME})
PYTHON_VERSION=3.7

current_dir = $(shell pwd)

VENV ?= ./../.venv
PG_PATH ?=../pg_database

venv = ${VENV}/py${PYTHON_VERSION}-${hash}

SHELL=bash

pg_port = 54320

default: update_venv
	
.PHONY: default

.DELETE_ON_ERROR:
${venv}: requirements.txt
	python${PYTHON_VERSION} -m venv ${venv}
	source ${venv}/bin/activate
	pip download -r ./requirements.txt -d ./.dependencies
	pip install -f ./.dependencies --no-index -r ./requirements.txt
	# python -m pip install -r ./requirements.txt 

.DELETE_ON_ERROR:
${venv}-offline: requirements.txt
	python${PYTHON_VERSION} -m venv ${venv}-offline
	source ${venv}-offline/bin/activate; pip install -f ./.dependencies --no-index -r ./requirements.txt


update_venv: requirements.txt ${venv}
	@rm -f ./.venv
	@ln -s ${venv} ./.venv
	@echo Success, to activate the development environment, run:
	@echo "   source .venv/bin/activate"

offline: requirements.txt ${venv}-offline
	@rm -f ./.venv
	@ln -s ${venv}-offline ./.venv
	@echo Success, to activate the development environment, run:
	@echo "   source .venv/bin/activate"

fetch_deps: 
	pip download --python-version 3.7 --no-deps  -r ./requirements.txt -d ./.dependencies

test:
ifeq ($(second), $(word 2, $(MAKECMDGOALS)))
	coverage erase
	python3 -m nose -v tests/*.py 
	@echo "#####################"
	@echo "##       OK        ##"
	@echo "#####################"
else
	python3 -m nose $(word 2, $(MAKECMDGOALS)) --nocapture
endif

long_test:
	python3 -m nose -v long_tests/*.py
	python3 -m nose -v long_tests/*/*.py
	rm -f best_parameters.json result.json

test_verbose:
	python3 -m nose --nocapture -v tests/*/*.py
	python3 -m nose --nocapture -v tests/*/*/*.py

integration_test:
	python3 -m nose -v integration_tests/*/*.py

install_deps:
	pip install --upgrade --force-reinstall -r requirements.txt



# database commands

pg_setup:
	@if ! command -v pg_ctl &> /dev/null; then \
		conda install -c anaconda postgresql -y; \
	fi

	@-initdb -D ${PG_PATH} --username=ashmat
	
	@if ! [ -f ${PG_PATH}/postmaster.pid ]; then \
		pg_ctl -o "-F -p ${pg_port}" -D ../pg_database \
				-l ../pg_logfile.log start; \
	fi

	@-createdb --port=${pg_port} --owner=ashmat lj_simulations
	
	@echo ""
	@echo ""
	@echo "Success! Connect to the database by"
	@echo "    psql -d lj_simulations -U ashmat -h localhost -p ${pg_port}"

pg_stop:
	pg_ctl -D ${PG_PATH}/pg_database stop


connect:
	psql -d lj_simulations -U ashmat -h localhost -p ${pg_port}