.PHONY: setup run test demo

setup:
	python -m venv .venv
	.venv/bin/pip install -e ".[dev]"

run:
	.venv/bin/python -m research_assistant.main

test:
	.venv/bin/pytest tests/ -v

demo:
	.venv/bin/pytest tests/test_demo.py -v
