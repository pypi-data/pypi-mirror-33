# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- SA core
# :Created:   sab 14 gen 2017 20:22:19 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017, 2018 Lele Gaifax
#

from __future__ import unicode_literals

import fixtures


class TestFake(fixtures.BaseTestCase):
    def test(self):
        assert 'id="test.FOO"' in self.index_html


SELECT = """

from sqlalchemy import bindparam

b = bindparam('ID')
'This is a parameter'

p = persons.alias('p')
Q = select([p.c.firstname, p.c.lastname]).where(p.c.id == b)
'This is a select statement'

"""

class TestSelect(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + SELECT

    def test(self):
        index_html = self.index_html
        assert 'This is a parameter' in index_html
        assert 'id="test.Q"' in index_html
        assert 'This is a select' in index_html
        assert '<span class="k">SELECT</span>' in index_html


INSERT = """

I = persons.insert().values(firstname='Foo', lastname='Bar')
'This is an insert statement'

"""

class TestInsert(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + INSERT

    def test(self):
        index_html = self.index_html
        assert 'id="test.I"' in index_html
        assert 'This is an insert' in index_html
        assert '<span class="k">INSERT</span>' in index_html


UPDATE = """

U = persons.update() \
           .values(firstname='Foo', lastname='Bar') \
           .where(persons.c.id == 1)
'This is an update statement'

"""

class TestUpdate(fixtures.BaseTestCase):
    TEST_PY = fixtures.BaseTestCase.TEST_PY + UPDATE

    def test(self):
        index_html = self.index_html
        assert 'id="test.U"' in index_html
        assert 'This is an update' in index_html
        assert '<span class="k">UPDATE</span>' in index_html
