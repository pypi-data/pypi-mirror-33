# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Test different dialects
# :Created:   mar 17 gen 2017 08:28:28 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

from __future__ import unicode_literals

import fixtures


SELECT = """

p = persons.alias('p')
Q = select([p.c.firstname, p.c.lastname]).where(func.char_length(p.c.firstname) > 1)
'This is a select statement'

"""

class TestLength_PG(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT
    SPHINX_CONF = fixtures.BaseTestCase.SPHINX_CONF + \
                  '\nautodoc_sa_dialect = "sqlalchemy.dialects.postgresql.dialect"'

    def test(self):
        index_html = self.index_html
        assert '<span class="k">char_length</span>' in index_html

class TestLength_SL(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT
    SPHINX_CONF = fixtures.BaseTestCase.SPHINX_CONF + \
                  '\nautodoc_sa_dialect = "sqlalchemy.dialects.sqlite.dialect"'

    def test(self):
        index_html = self.index_html
        assert '<span class="k">length</span>' in index_html
