"""
Static analysis submodule that defines the highly limited "strict"
subset of the Nada DSL syntax.
"""
# pylint: disable=wildcard-import,unused-wildcard-import,invalid-name
from __future__ import annotations
import ast
import richreports

try:
    from nada_dsl.audit.abstract import *
    from nada_dsl.audit.common import *
    from nada_dsl.audit.report import parse, enrich_fromaudits
except: # pylint: disable=bare-except # For Nada DSL Sandbox support.
    from abstract import *
    from common import *
    from report import parse, enrich_fromaudits

def _rules_restrictions_descendants(a):
    """
    Remove all rule attributes that are redundant because they occur in a
    an ancestor.
    """
    for a_ in ast.walk(a):
        if not isinstance(a_, (ast.Assign, ast.Assign)):
            if isinstance(audits(a_, 'rules'), (SyntaxRestriction, RuleInAncestor)):
                for a__ in ast.walk(a_):
                    if a__ != a_:
                        audits(a__, 'rules', RuleInAncestor())
                        audits(a__, 'types', delete=True)

def _types_binop_mult_add(t_l, t_r):
    """
    Determine the result type for multiplication and addition operations
    involving Nada DSL integers.
    """
    t = TypeErrorRoot('arguments must have integer types')
    if (t_l, t_r) == (Integer, Integer):
        t = Integer
    elif (t_l, t_r) == (Integer, PublicInteger):
        t = PublicInteger
    elif (t_l, t_r) == (PublicInteger, Integer):
        t = PublicInteger
    elif (t_l, t_r) == (Integer, SecretInteger):
        t = SecretInteger
    elif (t_l, t_r) == (SecretInteger, Integer):
        t = SecretInteger
    elif (t_l, t_r) == (PublicInteger, PublicInteger):
        t = PublicInteger
    elif (t_l, t_r) == (PublicInteger, SecretInteger):
        t = SecretInteger
    elif (t_l, t_r) == (SecretInteger, PublicInteger):
        t = SecretInteger
    elif (t_l, t_r) == (SecretInteger, SecretInteger):
        t = SecretInteger

    if isinstance(t_l, TypeError) or isinstance(t_r, TypeError):
        t = typeerror_demote(t)

    return t

def _types_compare(t_l, t_r):
    """
    Determine the result type for comparison operations involving Nada DSL
    integers.
    """
    t = TypeErrorRoot('arguments must have integer types')
    if (t_l, t_r) == (Integer, Integer):
        t = Boolean
    elif (t_l, t_r) == (Integer, PublicInteger):
        t = PublicBoolean
    elif (t_l, t_r) == (PublicInteger, Integer):
        t = PublicBoolean
    elif (t_l, t_r) == (Integer, SecretInteger):
        t = SecretBoolean
    elif (t_l, t_r) == (SecretInteger, Integer):
        t = SecretBoolean
    elif (t_l, t_r) == (PublicInteger, PublicInteger):
        t = PublicBoolean
    elif (t_l, t_r) == (PublicInteger, SecretInteger):
        t = SecretBoolean
    elif (t_l, t_r) == (SecretInteger, PublicInteger):
        t = SecretBoolean
    elif (t_l, t_r) == (SecretInteger, SecretInteger):
        t = SecretBoolean

    if isinstance(t_l, TypeError) or isinstance(t_r, TypeError):
        t = typeerror_demote(t)

    return t

def rules(a):
    """
    Mark all :obj:`ast` nodes as prohibited (as a starting point for a strict
    static analysis).
    """
    if isinstance(a, ast.Module):
        for a_ in ast.walk(a):
            audits(
                a_,
                'rules',
                SyntaxRestriction('use of this syntax is prohibited in strict mode')
            )

def types(a, env=None, func=False):
    """
    Infer types of :obj:`ast` where possible, adding the type (or error)
    information in node attributes (and removing syntax restriction attributes
    as appropriate).
    """
    # pylint: disable=too-many-statements,too-many-return-statements
    # pylint: disable=too-many-nested-blocks,too-many-branches
    # pylint: disable=too-many-locals
    env = {} if env is None else env

    # Handle cases in which the input node is a statement.
    if isinstance(a, ast.Module):
        rules_no_restriction(a)
        for a_ in a.body:
            env = types(a_, env, func)

        # Remove syntax restriction attributes that appear for descendants
        # of nodes that already have such attributes.
        _rules_restrictions_descendants(a)

        return env

    if isinstance(a, ast.ImportFrom):
        if (
            a.module == 'nada_dsl' and
            len(a.names) == 1 and a.names[0].name == '*' and a.names[0].asname is None and
            a.level == 0
        ):
            rules_no_restriction(a, recursive=True)
        return env

    if isinstance(a, ast.FunctionDef):
        if not func:
            if a.name == 'nada_main':
                rules_no_restriction(a)
                rules_no_restriction(a.args)

                # Create a local copy of the environment. Only the
                # original environment passed to this invocation
                # is returned.
                env_ = dict(env)
                for a_ in a.body:
                    env_ = types(a_, env_, func=True)

        return env

    if isinstance(a, ast.Assign):
        if len(a.targets) == 1 and isinstance(a.targets[0], ast.Name):
            rules_no_restriction(a)
            rules_no_restriction(a.targets[0])
            types(a.value, env, func)
            t = audits(a.value, 'types')
            if t is not None:
                audits(a, 'types', typeerror_demote(t))
                audits(a.targets[0], TypeInParent())
                if not isinstance(t, TypeError):
                    target = a.targets[0]
                    if isinstance(target, ast.Name):
                        var = target.id
                        env[var] = t

        return env

    if isinstance(a, ast.AnnAssign):
        if isinstance(a.target, ast.Name):
            rules_no_restriction(a)
            rules_no_restriction(a.target)
            types(a.value, env, func)
            t = audits(a.value, 'types')
            try:
                t_a = eval(ast.unparse(a.annotation)) # pylint: disable=eval-used
                rules_no_restriction(a.annotation, recursive=True)
            except: # pylint: disable=bare-except
                t_a = TypeErrorRoot('invalid type annotation')

            if isinstance(t, TypeError):
                audits(a, t)
                audits(a.target, t)
            else:
                t_u = unify(t_a, t)
                if t_u is None:
                    t = TypeErrorRoot('value type cannot be reconciled with type annotation')
                    audits(a, t)
                    audits(a.target, t)
                else:
                    t = t_u
                    audits(a, 'types', t)
                    audits(a.target, TypeInParent())
                    var = a.target.id
                    env[var] = t

        return env

    if isinstance(a, ast.Return):
        if func:
            rules_no_restriction(a)
            types(a.value, env, func)
        return env

    if isinstance(a, ast.For):
        rules_no_restriction(a)
        types(a.iter, env, func)
        t_i = audits(a.iter, 'types')
        if isinstance(a.target, ast.Name):
            rules_no_restriction(a.target)
            var = a.target.id
            audits(a.target, 'types', int)
            if isinstance(t_i, TypeError):
                pass # Allow the error to pass through.
            elif t_i == range:
                env[var] = int
                for a_ in a.body:
                    env = types(a_, env, func)
            else:
                audits(a.iter, 'types', TypeErrorRoot('iterable must be a range'))
        return env

    if isinstance(a, ast.Expr):
        types(a.value, env, func)
        if not isinstance(audits(a.value, 'rules'), SyntaxRestriction):
            rules_no_restriction(a)
        return env

    # Handle cases in which the input node is an expression.
    audits(a, 'types', TypeError('type cannot be determined'))

    if isinstance(a, ast.ListComp):
        rules_no_restriction(a)
        ts = {}
        for comprehension in a.generators:
            rules_no_restriction(comprehension)
            types(comprehension.iter, env, func)
            t_c = audits(comprehension.iter, 'types')
            if isinstance(comprehension.target, ast.Name):
                rules_no_restriction(comprehension.target)
                var = comprehension.target.id
                t = int
                if isinstance(t_c, TypeError):
                    pass # Allow the error to pass through.
                elif t_c == range:
                    rules_no_restriction(comprehension.iter)
                    ts[var] = t
                else:
                    t = TypeErrorRoot('iterable must be a range value')
                    audits(comprehension.iter, 'types', t)
                t = typeerror_demote(t)
                audits(comprehension.target, 'types', t)
        env_ = dict(env)
        for (var, t_) in ts.items():
            env_[var] = t_
        types(a.elt, env_, func)
        t_e = audits(a.elt, 'types')
        if t_e is not None and not isinstance(t_e, TypeError):
            audits(a, 'types', list[t_e])

    elif isinstance(a, ast.Call):
        ats = []
        kts = []
        for a_ in a.args:
            types(a_, env, func)
            ats.append(audits(a_, 'types'))
        for a_ in a.keywords:
            types(a_.value, env, func)
            kts.append(audits(a_.value, 'types'))

        if isinstance(a.func, ast.Attribute):
            types(a.func.value, env, func)
            t_v = audits(a.func.value, 'types')
            if a.func.attr == 'if_else':
                if len(a.args) == 2:
                    ts = ats
                    rules_no_restriction(a)
                    rules_no_restriction(a.func)
                    if t_v == Boolean:
                        if (
                            ts[0] in (Integer, PublicInteger, SecretInteger) and
                            ts[1] in (Integer, PublicInteger, SecretInteger)
                        ):
                            t = max(ts)
                        else:
                            t = TypeErrorRoot('branches must have the same integer type')
                    elif t_v == PublicBoolean:
                        if (
                            ts[0] in (Integer, PublicInteger, SecretInteger) and
                            ts[1] in (Integer, PublicInteger, SecretInteger)
                        ):
                            t = max(ts)
                        else:
                            t = TypeErrorRoot('branches must have the same integer type')
                    elif t_v == SecretBoolean:
                        if (
                            ts[0] in (Integer, PublicInteger, SecretInteger) and
                            ts[1] in (Integer, PublicInteger, SecretInteger)
                        ):
                            t = max(ts)
                        else:
                            t = TypeErrorRoot('branches must have the same integer type')
                    else:
                        t = TypeErrorRoot('condition must have a boolean type')

                    audits(a, 'types', t)
            elif a.func.attr == 'append':
                if len(a.args) == 1:
                    rules_no_restriction(a)
                    rules_no_restriction(a.func)
                    t_i = ats[0]
                    if t_v.__name__ == 'list':
                        audits(a, 'types', type(None))

        elif isinstance(a.func, ast.Name):
            if a.func.id == 'Party':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = TypeError('party requires name parameter (a string)')
                if (
                    len(a.args) == 0 and
                    len(a.keywords) == 1 and
                    a.keywords[0].arg == 'name'
                ):
                    rules_no_restriction(a.keywords[0])
                    if audits(a.keywords[0].value, 'types') == str:
                        t = Party
                elif (
                    len(a.args) == 1 and
                    len(a.keywords) == 0
                ):
                    rules_no_restriction(a.args[0])
                    if audits(a.args[0], 'types') == str:
                        t = Party
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'Input':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = TypeError('input requires name parameter (a string) and party parameter')
                if (
                    len(a.args) == 2 and
                    len(a.keywords) == 0
                ):
                    rules_no_restriction(a.args[0])
                    rules_no_restriction(a.args[1])
                    if (
                        audits(a.args[0], 'types') == str and
                        audits(a.args[1], 'types') == Party
                    ):
                        t = Input
                if (
                    len(a.args) == 1 and
                    len(a.keywords) == 1 and
                    a.keywords[0].arg == 'party'
                ):
                    rules_no_restriction(a.args[0])
                    rules_no_restriction(a.keywords[0])
                    if (
                        audits(a.args[0], 'types') == str and
                        audits(a.keywords[0].value, 'types') == Party
                    ):
                        t = Input
                if (
                    len(a.args) == 0 and
                    len(a.keywords) == 2 and
                    a.keywords[0].arg == 'name' and
                    a.keywords[1].arg == 'party'
                ):
                    rules_no_restriction(a.keywords[0])
                    rules_no_restriction(a.keywords[1])
                    if (
                        audits(a.keywords[0].value, 'types') == str and
                        audits(a.keywords[1].value, 'types') == Party
                    ):
                        t = Input
                if (
                    len(a.args) == 0 and
                    len(a.keywords) == 2 and
                    a.keywords[1].arg == 'name' and
                    a.keywords[0].arg == 'party'
                ):
                    rules_no_restriction(a.keywords[0])
                    rules_no_restriction(a.keywords[1])
                    if (
                        audits(a.keywords[1].value, 'types') == str and
                        audits(a.keywords[0].value, 'types') == Party
                    ):
                        t = Input
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'Output':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = TypeError(
                    'output requires value parameter, name parameter (a string), ' +
                    'and party parameter'
                )
                kwargs = {kw.arg: kw.value for kw in a.keywords}
                if len(a.args) == 0 and len(a.keywords) == 3:
                    if set(kwargs.keys()) == {'value', 'name', 'party'}:
                        for kw in a.keywords:
                            rules_no_restriction(kw)
                        if (
                            (
                                audits(kwargs['value'], 'types')
                                in
                                (SecretInteger, PublicInteger)
                            ) and
                            audits(kwargs['name'], 'types') == str and
                            audits(kwargs['party'], 'types') == Party
                        ):
                            t = Output
                elif len(a.args) == 1 and len(a.keywords) == 2:
                    if set(kwargs.keys()) == {'name', 'party'}:
                        for arg in a.args:
                            rules_no_restriction(arg)
                        for kw in a.keywords:
                            rules_no_restriction(kw)
                        if (
                            (
                                audits(a.args[0], 'types')
                                in
                                (SecretInteger, PublicInteger)
                            ) and
                            audits(kwargs['name'], 'types') == str and
                            audits(kwargs['party'], 'types') == Party
                        ):
                            t = Output
                elif len(a.args) == 2 and len(a.keywords) == 1:
                    if set(kwargs.keys()) == {'party'}:
                        for arg in a.args:
                            rules_no_restriction(arg)
                        for kw in a.keywords:
                            rules_no_restriction(kw)
                        if (
                            (
                                audits(a.args[0], 'types')
                                in
                                (SecretInteger, PublicInteger)
                            ) and
                            audits(a.args[1], 'types') == str and
                            audits(kwargs['party'], 'types') == Party
                        ):
                            t = Output
                elif len(a.args) == 3 and len(a.keywords) == 0:
                    for arg in a.args:
                        rules_no_restriction(arg)
                    for kw in a.keywords:
                        rules_no_restriction(kw)
                    if (
                        (
                            audits(a.args[0], 'types')
                            in
                            (SecretInteger, PublicInteger)
                        ) and
                        audits(a.args[1], 'types') == str and
                        audits(a.args[2], 'types') == Party
                    ):
                        t = Output
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'Integer':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = Integer
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != int
                ):
                    t = TypeError('expecting single argument (an integer)')
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'PublicInteger':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = PublicInteger
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != Input
                ):
                    t = TypeError('expecting single argument (an input object)')
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'SecretInteger':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = SecretInteger
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != Input
                ):
                    t = TypeError('expecting single argument (an input object)')
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'range':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = range
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != int
                ):
                    t = TypeErrorRoot('expecting single integer argument')
                    if isinstance(audits(a.args[0], 'types'), TypeError):
                        t = typeerror_demote(t)
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'str':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = str
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != int
                ):
                    t = TypeError('expecting single integer argument')
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

            elif a.func.id == 'sum':
                rules_no_restriction(a)
                rules_no_restriction(a.func)
                t = SecretInteger
                if (
                    len(a.args) != 1 or
                    audits(a.args[0], 'types') != list[SecretInteger]
                ):
                    t = TypeError('expecting argument of type list[SecretInteger]')
                audits(a, 'types', t)
                audits(a.func, 'types', TypeInParent())

    elif isinstance(a, ast.Subscript):
        rules_no_restriction(a)
        types(a.value, env, func)
        types(a.slice, env, func)
        t_v = audits(a.value, 'types')
        t_s = audits(a.slice, 'types')
        if (not isinstance(t_v, TypeError)) and (not isinstance(t_s, TypeError)):
            t = TypeErrorRoot('expecting list value and integer index')
            if t_v.__name__ == 'list' and t_s == int:
                if hasattr(t_v, '__args__') and len(t_v.__args__) == 1:
                    t = t_v.__args__[0]
                    audits(a, 'types', t)

    elif isinstance(a, ast.List):
        rules_no_restriction(a)
        for a_ in a.elts:
            types(a_, env, func)

        ts = [audits(a_, 'types') for a_ in a.elts]
        t = TypeError('lists must contain elements that are all of the same type')
        if len(set(ts)) == 0:
            t = list
        elif len(set(ts)) == 1:
            t = ts[0]
            if isinstance(t, TypeError):
                t = typeerror_demote(t)
            else:
                t = list[t]
        audits(a, 'types', t)

    elif isinstance(a, ast.BoolOp):
        rules_no_restriction(a)
        ts = []
        for a_ in a.values:
            types(a_, env, func)
            ts.append(audits(a_, 'types'))
        t = TypeErrorRoot('arguments must be boolean values')
        if all(t == bool for t in ts):
            t = bool
        elif any(isinstance(t, TypeError) for t in ts):
            t = typeerror_demote(t)
        audits(a, 'types', t)

    elif isinstance(a, ast.BinOp):
        types(a.left, env, func)
        types(a.right, env, func)
        t_l = audits(a.left, 'types')
        t_r = audits(a.right, 'types')
        if isinstance(a.op, ast.Mult):
            rules_no_restriction(a)
            t = _types_binop_mult_add(t_l, t_r)
            audits(a, 'types', t)
        elif isinstance(a.op, ast.Add):
            rules_no_restriction(a)
            t = TypeError('unsupported argument types')
            if t_l == str and t_r == str:
                t = str
            else:
                t = _types_binop_mult_add(t_l, t_r)
            audits(a, 'types', t)

    elif isinstance(a, ast.Compare):
        if len(a.comparators) != 1:
            audits(
                a,
                'rules',
                SyntaxRestriction('chained comparisons are prohibited in strict mode')
            )
        else:
            rules_no_restriction(a)
            types(a.left, env, func)
            types(a.comparators[0], env, func)
            t_l = audits(a.left, 'types')
            t_r = audits(a.comparators[0], 'types')
            if isinstance(
                a.ops[0],
                (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
            ):
                if t_l == int and t_r == int:
                    t = bool
                else:
                    t = _types_compare(t_l, t_r)
            audits(a, 'types', t)

    elif isinstance(a, ast.UnaryOp):
        types(a.operand, env, func)
        t = audits(a.operand, 'types')
        if isinstance(a.op, (ast.UAdd, ast.USub)):
            rules_no_restriction(a)
            if isinstance(t, TypeError):
                t = typeerror_demote(t)
            elif t in (int, Integer, PublicInteger, SecretInteger):
                pass
            else:
                t = TypeErrorRoot('argument must have an integer type')
            audits(a, 'types', t)

        elif isinstance(a.op, ast.Not):
            rules_no_restriction(a)
            if isinstance(t, TypeError):
                t = typeerror_demote(t)
            elif t == bool:
                pass
            else:
                t = TypeErrorRoot('argument must be a boolean value')
            audits(a, 'types', t)

    elif isinstance(a, ast.Name):
        rules_no_restriction(a)
        var = a.id
        audits(
            a,
            'types',
            env[var] if var in env else TypeError("name '" + var + "' is not defined")
        )

    elif isinstance(a, ast.Constant):
        if a.value in (False, True):
            rules_no_restriction(a)
            audits(a, 'types', bool)
        elif isinstance(a.value, int):
            rules_no_restriction(a)
            audits(a, 'types', int)
        elif isinstance(a.value, str):
            rules_no_restriction(a)
            audits(a, 'types', str)

    return env # Always return the environment.

def strict(source: str) -> richreports.report:
    """
    Take a Python source file representing a Nada DSL program, statically
    analyze it (against the "strict" Nada DSL subset), and generate an
    interactive HTML report detailing the results.
    """
    (atok, skips) = parse(source)
    root = atok.tree

    # Perform the static analyses.
    rules(root)
    types(root)

    # Perform the abstract execution.
    #root.body.append(ast.Expr(ast.Call(ast.Name('nada_main', ast.Load()), [], [])))
    #ast.fix_missing_locations(root)
    #exec(compile(root, path, 'exec'))

    # Add the results of the analyses to the report and ensure each line is
    # wrapped as an HTML element.
    report = richreports.report(source, line=1, column=0)
    enrich_fromaudits(report, atok)
    for (i, line) in enumerate(report.lines):
        if i in skips:
            report.enrich(
                (i + 1, 0), (i + 1, len(line) - 1),
                '<span class="rules-SyntaxError">', '</span>',
                skip_whitespace=True
            )
            report.enrich(
                (i + 1, 0), (i + 1, len(line) - 1),
                '<span class="detail" data-detail="SyntaxError">', '</span>',
                skip_whitespace=True
            )
        report.enrich((i + 1, 0), (i + 1, len(line)), '<div>', '</div>')

    return report
