
doc:
	python -m pip install '.[docs]' && sphinx-build docs docs/_build

release:
	pip install --upgrade build wheel
	python -m build --no-isolation

lint: 
	pylint nada_dsl/

test-dependencies:
	pip install .'[test]'

test: test-dependencies
	pytest