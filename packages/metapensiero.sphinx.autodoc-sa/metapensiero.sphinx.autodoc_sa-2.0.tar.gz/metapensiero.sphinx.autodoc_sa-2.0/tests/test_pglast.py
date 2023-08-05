# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Test pglast prettifier
# :Created:   lun 07 ago 2017 16:44:22 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

import sys

import pytest

import fixtures


SELECT = """

from sqlalchemy import bindparam

b = bindparam('ID')
'This is a parameter'

p = persons.alias('p')
p2 = persons.alias('p2')
Q = select([p.c.firstname, p.c.lastname,
            select([p2.c.lastname])\
            .where(p2.c.id == p.c.id).as_scalar()]) \
    .where(p.c.id != 0) \
    .where(func.check_name(p.c.firstname))
'This is a silly select statement'

"""

@pytest.mark.skipif(sys.version_info < (3,6), reason="pglast requires at least Py3.6")
class Test_PG_Query_Prettify(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT
    SPHINX_CONF = fixtures.BaseTestCase.SPHINX_CONF + \
                  '\nautodoc_sa_dialect = "sqlalchemy.dialects.postgresql.dialect"' + \
                  '\nautodoc_sa_prettifier = "pglast"' + \
                  '\nautodoc_sa_prettifier_options = dict(compact_lists_margin=80)' + \
                  '\nautodoc_sa_pygments_lang = "postgresql"'

    def test(self):
        index_html = self.index_html
        with open('/tmp/satest.html','w', encoding='utf-8') as f:
            f.write(index_html)
        assert '     <span class="p">,</span> <span class="n">p</span>' in index_html
        assert '     <span class="p">,</span> <span class="p">(</span><span class="k">SELECT</span>' in index_html
        assert '        <span class="k">FROM</span> <span class="n">persons</span>' in index_html
        assert '<span class="p">)</span> <span class="k">AND</span> <span class="n">check_name</span>' in index_html
