"""Export classes and functions for Nada DSL auditing component."""
import argparse

from nada_dsl.audit.abstract import *
from nada_dsl.audit.report import html
from nada_dsl.audit.strict import strict

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs=1, help='Nada DSL source file path')
    parser.add_argument('--strict', action='store_true', required=True)
    args = parser.parse_args()
    path = args.path[0]

    with open(path, 'r', encoding='UTF-8') as file:
        source = file.read()
        report = strict(source)

    with open(path[:-2] + 'html', 'w', encoding='UTF-8') as file:
        file.write(html(report))
