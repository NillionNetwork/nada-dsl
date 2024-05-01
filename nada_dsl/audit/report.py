"""
Common functions that Nada DSL static analysis submodules can use to build
interactive HTML reports.
"""
# pylint: disable=wildcard-import,unused-wildcard-import,invalid-name
from __future__ import annotations
from typing import List, Tuple
import ast
import asttokens
import richreports
import parsial

try:
    from nada_dsl.audit.abstract import *
    from nada_dsl.audit.common import *
except: # pylint: disable=bare-except # For Nada DSL Sandbox support.
    from abstract import *
    from common import *

def parse(source: str) -> Tuple[asttokens.ASTTokens, List[int]]:
    """
    Parse a Python source string that represents a Nada DSL program
    and return both its abstract syntax tree and a list of which lines
    were skipped by the partial parser due to syntax errors.
    """
    lines = source.split('\n')
    (_, slices) = parsial.parsial(ast.parse)(source)
    lines_ = [l[s] for (l, s) in zip(lines, slices)]
    skips = [i for i in range(len(lines)) if len(lines[i]) != len(lines_[i])]
    return (asttokens.ASTTokens('\n'.join(lines_), parse=True), skips)

def locations(report_, asttokens_, a):
    """
    Return the starting and ending locations corresponding to an :obj:`ast`
    node.
    """
    ((start_line, start_column), (end_line, end_column)) = \
        asttokens_.get_text_positions(a, True)

    # Skip any whitespace when determining the starting location.
    line = report_.lines[start_line - 1]
    while line[start_column] == ' ' and start_column < len(line):
        start_column += 1

    return (
        richreports.location((start_line, start_column)),
        richreports.location((end_line, end_column - 1))
    )

def type_to_str(t):
    """
    Convert a type and/or type error :obj:`ast` node attribute into a
    human-readable string.
    """
    if hasattr(t, '__name__'):
        if t.__name__ == 'list':
            if hasattr(t, '__args__'):
                return 'list[' + type_to_str(t.__args__[0]) + ']'
            return 'list'

        return str(t.__name__)

    if isinstance(t, TypeError):
        return str('TypeError: ' + str(t))

    return str('TypeError: ' + 'type cannot be determined')

def enrich_from_type(report_, type_, start, end):
    """
    Enrich a range within a report according to the supplied type attribute.
    """
    if (
        type_ in (
            bool, int, str, range,
            Party, Input, Output,
            Integer, PublicInteger, SecretInteger,
            Boolean, PublicBoolean, SecretBoolean
        )
        or
        (
            hasattr(type_, '__name__') and
            type_.__name__ == 'list'
        )
    ):
        t_str = type_to_str(type_)
        report_.enrich(
            start, end,
            '<span class="types-' + t_str + '">', '</span>',
            True,
            True
        )

    if isinstance(type_, (TypeError, TypeErrorRoot)):
        report_.enrich(
            start, end,
            '<span class="types-' + type_.__class__.__name__ + '">', '</span>',
            True,
            True
        )

def enrich_syntaxrestriction(report_, r, start, end):
    """
    Enrich a range within a report according to the supplied syntax restriction.
    """
    report_.enrich(
        start, end,
        '<span class="rules-SyntaxRestriction">', '</span>',
        enrich_intermediate_lines=True,
        skip_whitespace=True
    )
    report_.enrich(
        start, end,
        '<span class="detail" data-detail="SyntaxRestriction: ' + str(r) + '">',
        '</span>',
        enrich_intermediate_lines=True,
        skip_whitespace=True
    )

def enrich_keyword(report_, start, length):
    """
    Enrich a range within a report corresponding to a Python keyword.
    """
    (start_line, start_column) = start
    report_.enrich(
        (start_line, start_column), (start_line, start_column + length),
        '<span class="keyword">', '</span>',
        enrich_intermediate_lines=True,
        skip_whitespace=True
    )

def enrich_fromaudits(report_: richreports.report, atok) -> richreports.report:
    """
    Enrich a report containing the source code of a Nada DSL program using the
    static analysis attributes found within an :obj:`ast` instance.
    """
    # pylint: disable=too-many-statements,too-many-branches
    for a in ast.walk(atok.tree):
        r = audits(a, 'rules')
        t = audits(a, 'types')

        if isinstance(a, (ast.Assign, ast.AnnAssign)):
            target = a.targets[0] if hasattr(a, 'targets') else a.target
            (start, end) = locations(report_, atok, target)
            if isinstance(r, SyntaxRestriction):
                enrich_syntaxrestriction(report_, r, start, end)
            else:
                enrich_from_type(report_, t, start, end)
                t_str = (
                    type_to_str(t)
                    if not isinstance(t, TypeError) else
                    'TypeError: ' + str(t)
                )
                report_.enrich(
                    start, end,
                    '<span class="detail" data-detail="' + t_str + '">', '</span>',
                    True
                )

        elif isinstance(r, SyntaxRestriction):
            (start, end) = locations(report_, atok, a)
            enrich_syntaxrestriction(report_, r, start, end)

        elif isinstance(r, RuleInAncestor):
            pass # This node will be wrapped by an ancestor's enrichment.

        elif isinstance(a, ast.ImportFrom):
            (start, _) = locations(report_, atok, a)
            enrich_keyword(report_, start, 4)

        elif isinstance(a, ast.Return):
            (start, end) = locations(report_, atok, a)
            if isinstance(r, SyntaxRestriction):
                enrich_syntaxrestriction(report_, r, start, end)
            else:
                enrich_keyword(report_, start, 6)
                t = audits(a.value, 'types')
                report_.enrich(
                    start, start + (0, 6),
                    '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                    True
                )

        elif isinstance(a, ast.For):
            (start, end) = locations(report_, atok, a)
            enrich_keyword(report_, start, 3)
            (_, start) = locations(report_, atok, a.target)
            (end, _) = locations(report_, atok, a.iter)
            report_.enrich(
                start + (0, 1), end - (0, 1),
                '<span class="keyword">', '</span>',
                enrich_intermediate_lines=True,
                skip_whitespace=True
            )

        elif isinstance(a, ast.FunctionDef):
            (start, end) = locations(report_, atok, a)
            enrich_keyword(report_, start, 3)
            if isinstance(r, SyntaxRestriction):
                enrich_syntaxrestriction(report_, r, start, end)

        elif isinstance(a, ast.ListComp):
            for generator in a.generators:
                (start, _) = locations(report_, atok, generator)
                enrich_keyword(report_, start, 3)
                (_, start) = locations(report_, atok, generator.target)
                (end, _) = locations(report_, atok, generator.iter)
                report_.enrich(
                    start + (0, 1), end - (0, 1),
                    '<span class="keyword">', '</span>',
                    enrich_intermediate_lines=True,
                    skip_whitespace=True
                )

        elif isinstance(a, ast.Call):
            (start, end) = locations(report_, atok, a.func)
            if isinstance(a.func, ast.Attribute):
                (_, start) = locations(report_, atok, a.func.value)
                start = start + (0, 1)
            enrich_from_type(report_, t, start, end)
            report_.enrich(
                start, end,
                '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                True
            )

        elif isinstance(a, ast.BoolOp):
            for i in range(len(a.values) - 1):
                (left, right) = (a.values[i], a.values[i + 1])
                (_, end) = locations(report_, atok, left)
                (start, _) = locations(report_, atok, right)
                (start, end) = (end + (0, 1), start - (0, 1))
                report_.enrich(start, end, '<b>', '</b>', True, True)
                enrich_from_type(report_, t, start, end)
                report_.enrich(
                    start, end,
                    '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                    True,
                    True
                )

        elif isinstance(a, ast.BinOp):
            (_, end) = locations(report_, atok, a.left)
            (start, _) = locations(report_, atok, a.right)
            (start, end) = (end + (0, 1), start - (0, 1))
            enrich_from_type(report_, t, start, end)
            report_.enrich(
                start, end,
                '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                True,
                True
            )

        elif isinstance(a, ast.Compare):
            (_, end) = locations(report_, atok, a.left)
            (start, _) = locations(report_, atok, a.comparators[0])
            (start, end) = (end + (0, 1), start - (0, 1))
            enrich_from_type(report_, t, start, end)
            report_.enrich(
                start, end,
                '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                True,
                True
            )

        elif isinstance(a, ast.UnaryOp):
            (start, _) = locations(report_, atok, a)
            (end, _) = locations(report_, atok, a.operand)
            end = end - (0, 2)
            enrich_from_type(report_, t, start, end)
            if isinstance(a.op, ast.Not):
                report_.enrich(start, end, '<b>', '</b>', True)
            report_.enrich(
                start, end,
                '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                True
            )

        elif isinstance(a, ast.Constant):
            (start, end) = locations(report_, atok, a)
            if isinstance(r, SyntaxRestriction):
                enrich_syntaxrestriction(report_, r, start, end)
            else:
                enrich_from_type(report_, t, start, end)
                report_.enrich(
                    start, end,
                    '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                    True
                )

        elif isinstance(a, ast.Name):
            (start, end) = locations(report_, atok, a)
            if isinstance(r, SyntaxRestriction):
                enrich_syntaxrestriction(report_, r, start, end)
            else:
                if t is not None and not isinstance(t, TypeInParent):
                    enrich_from_type(report_, t, start, end)
                    report_.enrich(
                        start, end,
                        '<span class="detail" data-detail="' + type_to_str(t) + '">', '</span>',
                        True
                    )

def html(report: richreports.report) -> str:
    """
    Return a self-contained CSS/HTML document corresponding to a report.
    """
    head = '    ' + '''
    <style>
      body { font-family:Monospace; white-space;pre; }
      .keyword { font-weight:bold; color:#000000; }
      .rules-SyntaxError { background-color:#FFFF00; color:#555555; }
      .rules-SyntaxRestriction { background-color:#CCCC00; font-weight:bold; color:#000000; }
      .types-TypeError { background-color:#FFCCCB; font-weight:bold; color:#B22222; }
      .types-TypeErrorRoot { background-color:#FF0000; font-weight:bold; color:#FFFFFF ; }
      .types-bool { font-weight:bold; color:#000000; }
      .types-int { font-weight:bold; color:#000000; }
      .types-str { font-weight:bold; color:#000000; }
      .types-Party { font-weight:bold; color:#d45cd6; }
      .types-Input { font-weight:bold; color:#DAA520; }
      .types-Output { font-weight:bold; color:#DAA520; }
      .types-Integer { font-weight:bold; color:#009900; }
      .types-Integer { font-weight:bold; color:#009900; }
      .types-PublicInteger { font-weight:bold; color:#009900; }
      .types-SecretInteger { font-weight:bold; color:#0000FF; }
      .types-Boolean { font-weight:bold; color:#009900; }
      .types-PublicBoolean { font-weight:bold; color:#009900; }
      .types-SecretBoolean { font-weight:bold; color:#0000FF; }
      div { height:18px; line-height:18px; white-space:pre; }
      div span { padding-top:3px; padding-bottom:3px; line-height:18px; cursor:pointer; }
      .detail { cursor:pointer; }
      .detail:hover { background-color:#DDDDDD; }
      #detail {
        display:none;
        position:absolute;
        padding:12px;
        background-color:#000000;
        color:#FFFFFF;
      }
    </style>
    '''.strip() + '\n'

    script = '    ' + '''
    <script>
      window.onload = function () {
        const elements = document.getElementsByClassName("detail");
        for (let i = 0; i < elements.length; i++) {
          const element = elements[i];
          element.addEventListener("mouseover", function (event) {
            const detail = document.getElementById("detail");
            detail.style.display = "block";
            detail.style.top = element.offsetTop + 24 + "px";
            detail.style.left = (
              element.offsetLeft +
              element.getBoundingClientRect().width -
              16
            ) + "px";
            detail.innerHTML = element.dataset.detail;
          });
          element.addEventListener("mouseout", function (event) { 
            const detail = document.getElementById("detail");
            detail.style.display = "none";
          });
        }
      };
    </script>
    '''.strip() + '\n'

    return (
        '<html>\n' +
        '  <head>\n' + 
        head +
        '  </head>\n' +
        '  <body>\n  <div id="detail"></div>\n' +
        report.render() +
        '\n  </body>\n' +
        script +
        '</html>\n'
    )
