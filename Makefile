
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
