
doc:
	uv run sphinx-build docs docs/_build

release:
	pip install --upgrade build wheel
	python -m build --no-isolation

lint: 
	uv run pylint nada_dsl/

format:
	uv run ruff format

format-check:
	uv run ruff format --check

# TODO fix all check errors
ruff-check:
	uv run ruff check

test-dependencies:
	pip install .'[test]'

test: test-dependencies
	pytest

# Build protocol buffers definitions. 
build_proto:
	nada_mir/scripts/gen_proto.sh