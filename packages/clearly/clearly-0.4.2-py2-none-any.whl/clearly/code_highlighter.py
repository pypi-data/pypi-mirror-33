# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals

import six

from .safe_compiler import CallDescriptor
from .utils.colors import colors
from .utils.text import force_text

SEPARATOR = colors.RED(', ')
KWARGS_SEPARATOR = colors.RED('=')
DICT_SEPARATOR = colors.RED(': ')
NONE = colors.CYAN('None')

try:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    unicode
except:
    def unicode(x):
        return str(x)


def typed_code(p, wrap=True):
    if p is None:
        return NONE

    if isinstance(p, bool):
        return colors.CYAN(str(p))

    if isinstance(p, six.string_types):
        p = force_text(p)
        if "'" in p and '"' not in p:
            escape = '"'
        else:
            escape = "'"
            p = p.replace("'", "\\'")
        return colors.YELLOW('{c}{p}{c}'.format(p=p, c=escape))

    if isinstance(p, six.integer_types + (float,)):
        return colors.GREEN(str(p))

    if isinstance(p, CallDescriptor):
        func_args = typed_code(p.args, wrap=False) if p.args else ''
        if p.kwargs:
            if p.args:
                func_args += SEPARATOR
            func_args += typed_code(p.kwargs, wrap=False)
        return '{}({})'.format(force_text(p.name), func_args)

    if isinstance(p, list):
        f = '[{}]' if wrap else '{}'
        return f.format(SEPARATOR.join(typed_code(x) for x in p))

    if isinstance(p, set):
        return '{{{}}}'.format(typed_code(sorted(p, key=lambda x: unicode(x)), wrap=False))

    if isinstance(p, tuple):
        if wrap:
            f = '({})' if len(p) != 1 else '({},)'
        else:
            f = '{}'
        return f.format(SEPARATOR.join(typed_code(x) for x in p))

    if isinstance(p, dict):
        if wrap:
            f = '{{{}}}'
            sep = DICT_SEPARATOR

            def key(k):
                return typed_code(k)
        else:
            f = '{}'
            sep = KWARGS_SEPARATOR

            def key(k):
                return colors.ORANGE(k)

        return f.format(
            SEPARATOR.join('{}{}{}'.format(key(k), sep, typed_code(v))
                           for k, v in p.items()))

    return force_text(repr(p))
