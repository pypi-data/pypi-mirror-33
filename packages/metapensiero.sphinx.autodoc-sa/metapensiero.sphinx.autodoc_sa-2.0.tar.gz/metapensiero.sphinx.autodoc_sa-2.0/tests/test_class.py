# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Test with autoclass
# :Created:   mar 17 gen 2017 09:08:45 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

from __future__ import unicode_literals

import fixtures


SELECT = """

Q = select([persons])

class Class:
    'This is a class'

    SELECT = Q
    'This is a select statement'

"""

class TestClass(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT
    INDEX_TXT = """\
Autodoc SA test
===============

.. autoclass:: test.Class
   :members:

"""

    def test(self):
        index_html = self.index_html
        assert 'id="test.Class.SELECT"' in index_html
        assert 'This is a select' in index_html
        assert '<span class="k">SELECT</span>' in index_html
