
nada-dsl-doc:
	python -m pip install '.[docs]' && sphinx-build docs docs/_build

release:
	pip install --upgrade build wheel
	python -m build --no-isolation