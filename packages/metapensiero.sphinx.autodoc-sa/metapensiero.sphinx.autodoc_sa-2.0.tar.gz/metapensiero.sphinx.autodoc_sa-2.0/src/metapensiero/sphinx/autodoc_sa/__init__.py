# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Pretty print canned SQLAlchemy statements
# :Created:   mar 11 ago 2015 11:44:44 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016, 2017, 2018 Lele Gaifax
#

from sphinx.ext import autodoc
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.elements import BindParameter
from sqlalchemy.orm import Query


try:
    from sqlparse import format as sqlparse_format
except ImportError:
    sqlparse_prettifier = None
else:
    def sqlparse_prettifier(sql, **options):
        if 'reindent' not in options:
            options['reindent'] = True
        return sqlparse_format(sql, **options)

try:
    from pglast import prettify
except ImportError:
    pglast_prettifier = None
else:
    def pglast_prettifier(sql, **options):
        return prettify(sql, **options)


dialect = None

def select_sa_dialect(app):
    global dialect
    classname = app.config.autodoc_sa_dialect
    if classname:
        if isinstance(classname, str):
            modulename, classname = classname.rsplit('.', 1)
            module = __import__(modulename, fromlist=[classname])
            dialect = getattr(module, classname)()
        else:
            dialect = classname
    else:
        dialect = None


future_param = object()


def format_value(value):
    from uuid import UUID

    if isinstance(value, UUID):
        value = str(value)

    result = repr(value)

    if len(result) > 50:
        result = result[:20] + ' … ' + result[-20:]

    return result


def format_numeric_param(position, prefix, args, match):
    key = int(match.group(1))
    value = args[key-1]
    if value is future_param:
        return '%s%s' % (prefix, next(position))
    else:
        return format_value(value)


def format_named_param(args, match):
    key = match.group(1)
    value = args[key]
    if value is future_param:
        return ':' + key
    else:
        return format_value(value)


def interpolate_sa_params(compiled_stmt):
    from functools import partial
    from itertools import count
    from re import escape, sub

    sql = compiled_stmt.string

    # This is a dirty hack, at best: SA injects bindparams by its own, to pass literal values
    # to the DB; here we try to "simplify" the query, replacing them with their known values,
    # leaving "real" bindparams (that is, the ones that developers coded in the query using
    # bindparam() explicitly. That is bad and errorprone, but after all we just want to pretty
    # print the statement for documentation purposes and you know, nobody RTFM anyway...
    #
    # Things may change in the future, see
    # https://bitbucket.org/zzzeek/sqlalchemy/issues/4024/mention-the-advanced-technique-to-have-raw

    params = {}
    for bp, bn in compiled_stmt.bind_names.items():
        if bp.key.startswith('%('):
            params[bn] = bp.value
        else:
            params[bn] = future_param

    if params:
        pstyle = dialect.paramstyle if dialect else 'pyformat'
        if pstyle == 'numeric':
            args = tuple(params[p] for p in compiled_stmt.positiontup)
            ptemplate = compiled_stmt.sql_compiler.bindtemplate
            format = partial(format_numeric_param, count(1), ptemplate[0])
            pregexp = r'%s(\d+)' % escape(ptemplate[0])
        elif pstyle == 'qmark':
            # Paramstyle not implemented, sorry
            return sql
        elif pstyle == 'pyformat':
            args = params
            format = format_named_param
            pregexp = r'%%\((%s)\)s' % '|'.join(args.keys())
        elif pstyle == 'named':
            args = params
            format = format_named_param
            pregexp = r':(%s)' % '|'.join(args.keys())

        sql = sub(pregexp, lambda m: format(args, m), sql)

    return sql


def stringify(env, stmt):
    how = env.config.autodoc_sa_prettifier
    if how == 'sqlparse':
        prettifier = sqlparse_prettifier
    elif how == 'pglast':
        prettifier = pglast_prettifier
    else:
        prettifier = None

    if isinstance(stmt, Query):
        stmt = stmt.statement

    try:
        sql = interpolate_sa_params(stmt.compile(dialect=dialect))
    except Exception as e:
        env.warn(env.docname,
                 "Parameters interpolation raised an error, keeping bogus statement: %s"
                 % e)
        sql = str(stmt)

    if prettifier is not None:
        try:
            sql = prettifier(sql, **env.config.autodoc_sa_prettifier_options)
        except Exception as e:
            env.warn(env.docname,
                     "SQL prettification raised an error, keeping the original: %s"
                     % e)
            pass

    return sql


class AttributeDocumenter(autodoc.AttributeDocumenter):
    """
    Customized AttributeDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.AttributeDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ClassLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.AttributeDocumenter.add_content(self, more_content, no_docstring)
        if ((isinstance(self.object, (ClauseElement, Query))
             and not isinstance(self.object, BindParameter))):
            sql = stringify(self.env, self.object)
            self.add_line("", "")
            lang = self.env.config.autodoc_sa_pygments_lang
            self.add_line(".. code-block:: %s" % lang, "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


class DataDocumenter(autodoc.DataDocumenter):
    """
    Customized DataDocumenter that knows about SA Select
    """

    def add_directive_header(self, sig):
        if not isinstance(self.object, (ClauseElement, Query)):
            autodoc.DataDocumenter.add_directive_header(self, sig)
        else:
            autodoc.ModuleLevelDocumenter.add_directive_header(self, sig)

    def add_content(self, more_content, no_docstring=False):
        autodoc.DataDocumenter.add_content(self, more_content, no_docstring)
        if ((isinstance(self.object, (ClauseElement, Query))
             and not isinstance(self.object, BindParameter))):
            sql = stringify(self.env, self.object)
            self.add_line("", "")
            lang = self.env.config.autodoc_sa_pygments_lang
            self.add_line(".. code-block:: %s" % lang, "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")


def setup(app):
    "Setup the Sphinx environment."

    from sphinx.config import ENUM
    from sphinx.application import directives

    # Brute force: remove already registered directives, to avoid pointless warning
    del directives._directives['autoattribute']
    del directives._directives['autodata']

    app.add_autodocumenter(AttributeDocumenter)
    app.add_autodocumenter(DataDocumenter)
    app.add_config_value('autodoc_sa_dialect', None, True)
    app.add_config_value('autodoc_sa_prettifier', 'sqlparse', True,
                         ENUM('sqlparse', 'pglast'))
    app.add_config_value('autodoc_sa_prettifier_options', {}, True)
    app.add_config_value('autodoc_sa_pygments_lang', 'sql', True)
    app.connect('builder-inited', select_sa_dialect)
