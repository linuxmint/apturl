import unittest

from AptUrl.Helpers import parse_pkg


class Candidate:
    def __init__(self, descr):
        self.description = descr
        self.homepage = None


class MockPkg:
    def __init__(self, descr):
        self.candidate = Candidate(descr)


class HelpersTest(unittest.TestCase):
    def test_parse_pkg(self):
        pkgobj = MockPkg("summary\ndescr\n")
        self.assertEqual(parse_pkg(pkgobj), ('summary','descr\n',None))
        pkgobj = MockPkg("summary only")
        self.assertEqual(parse_pkg(pkgobj), ('summary only','',None))
