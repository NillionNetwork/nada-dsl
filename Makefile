
doc:
	uv run sphinx-build docs docs/_build

release:
	pip install --upgrade build wheel
	python -m build --no-isolation

lint: 
	uv run pylint nada_dsl/

test-dependencies:
	pip install .'[test]'

test: test-dependencies
	pytest

# Build protocol buffers definitions. 
build_proto:
	nada_mir/scripts/gen_proto.sh