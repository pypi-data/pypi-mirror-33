# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Test for the ORM side
# :Created:   mar 17 gen 2017 00:25:10 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

import fixtures


SELECT = """

Q = orm.Query(Person)
'This is an ORM query'

"""

class TestSelect(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT

    def test(self):
        index_html = self.index_html
        assert 'id="test.Q"' in index_html
        assert 'This is an ORM query' in index_html
        assert '<span class="k">SELECT</span>' in index_html
