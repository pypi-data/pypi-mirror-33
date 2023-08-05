# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.autodoc_sa -- Fixtures used by the test suite
# :Created:   lun 22 feb 2016 14:18:21 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from __future__ import unicode_literals

from io import open
from locale import getpreferredencoding
from os.path import join
import shutil
import subprocess
import tempfile
import unittest


USER_ENCODING = getpreferredencoding() or "UTF-8"

DEFAULT_SPHINX_CONF = """\
import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
extensions = ['sphinx.ext.autodoc', 'metapensiero.sphinx.autodoc_sa']
source_suffix = '.txt'
master_doc = 'index'
"""

DEFAULT_INDEX_TXT = """\
Autodoc SA test
===============

.. automodule:: test
   :members:
"""


DEFAULT_TEST_PY = """\
from sqlalchemy import Column, Date, Integer, MetaData, String, Table, func, orm, select

metadata = MetaData()

persons = Table('persons', metadata,
                Column('id', Integer, primary_key=True),
                Column('firstname', String),
                Column('lastname', String),
                Column('birthdate', Date),
                )

class Person(object):
    def __init__(self, firstname, lastname, birthdate):
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate

orm.mapper(Person, persons)

FOO = None
'Bar'
"""


class TestSphinx(object):
    SPHINX_BUILD = 'sphinx-build'
    SPHINX_BUILD_OPTS = ('-b', 'html', '-q', '-d', '_build/doctrees', '.', '_build/html')

    def __init__(self, db_opts=None):
        self.db_opts = db_opts
        self.directory = tempfile.mkdtemp()

    def remove(self):
        shutil.rmtree(self.directory)

    def build(self, contents):
        from textwrap import dedent

        for filename, content in contents.items():
            with open(join(self.directory, filename), 'w', encoding='utf-8') as f:
                f.write(dedent(content))

        cmd = [self.SPHINX_BUILD]
        cmd.extend(self.SPHINX_BUILD_OPTS)
        try:
            output = subprocess.check_output(cmd, cwd=self.directory, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.build_error = e.output.decode(USER_ENCODING)
        else:
            output = output.decode(USER_ENCODING)
            self.build_error = output or None
        return self.build_error

    def get_artifact(self, name):
        fname = join(self.directory, '_build', 'html', name)
        with open(fname, encoding='utf-8') as f:
            return f.read()


class BaseTestCase(unittest.TestCase):
    SPHINX_CONF = DEFAULT_SPHINX_CONF
    "The configuration for the Sphinx environment"

    INDEX_TXT = DEFAULT_INDEX_TXT
    "The entry point of the documentation"

    TEST_PY = DEFAULT_TEST_PY
    "The test module"

    OTHER_FILES = ()
    "A possible sequence of ``(filename, content)`` tuples"

    @classmethod
    def contents(cls):
        yield 'conf.py', cls.SPHINX_CONF
        yield 'index.txt', cls.INDEX_TXT
        test_py = getattr(cls, 'TEST_PY', None)
        if test_py is not None:
            yield 'test.py', test_py
        for fname, content in cls.OTHER_FILES:
            yield fname, content

    @classmethod
    def setUpClass(cls):
        cls.sphinx = TestSphinx()
        cls.sphinx.build({filename: content for filename, content in cls.contents()})

    @classmethod
    def tearDownClass(cls):
        cls.sphinx.remove()

    @property
    def build_error(self):
        return self.sphinx.build_error

    def setUp(self):
        self.assertIsNone(self.build_error)

    def build(self, contents):
        return self.sphinx.build(contents)

    def get_artifact(self, name):
        return self.sphinx.get_artifact(name)

    @property
    def index_html(self):
        return self.get_artifact('index.html')
