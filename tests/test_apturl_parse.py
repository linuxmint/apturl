import unittest

from AptUrl import Parser


class UrlTests(unittest.TestCase):
    mapping = { 'kernel':"2.6.23-17-generic",
                'distro':"hardy" }

    testValues = ( ('apt:3ddesktop', [{'package':'3ddesktop',
                                      'schema': 'apt'}] ),
                   ('apt://3dchess', [{'package':'3dchess',
                                      'schema': 'apt'}] ),
                   ('apt+http://launchpad.net/~mvo/ppa?package=2vcard',
                    [{'package':'2vcard', 'schema': 'apt+http',
                     'repo_url': 'http://launchpad.net/~mvo/ppa',
                     'dist': '/' }] ),
                   ('apt+http://archive.canonical.com?package=acroread?dist=feisty?section=commercial',
                    [{'package':'acroread', 'schema': 'apt+http',
                     'repo_url': 'http://archive.canonical.com',
                     'dist': 'feisty', 'section': ['commercial']}] ),
                   ('apt+http://archive.canonical.com?package=acroread?keyfile=ppa-key',
                    [{'package':'acroread', 'schema': 'apt+http',
                     'repo_url': 'http://archive.canonical.com',
                     'keyfile': 'ppa-key' }]),
                   ('apt:2vcard?minver=1.0',
                    [{'package':'2vcard', 'schema': 'apt',
                     'minver': '1.0' }]),
                   ('apt:owl,newbiedoc,python-pykaraoke?dist=gutsy',
                    [{'package':'owl', 'schema':'apt'},
                    {'package':'newbiedoc', 'schema':'apt'},
                    {'package':'python-pykaraoke', 'schema':'apt', 'dist':'gutsy'}]),
                   ('apt:python-pykaraoke?dist=gutsy,owl,newbiedoc',
                    [{'package':'python-pykaraoke', 'schema':'apt', 'dist':'gutsy'},
                    {'package':'owl', 'schema':'apt'},
                    {'package':'newbiedoc', 'schema':'apt'}]),
                   ('apt:cdda2wav?section=multiverse',
                    [{'package':'cdda2wav', 'section':['multiverse']}]),
                   ('apt:java?section=multiverse?section=universe',
                    [{'package':'java', 'section':['multiverse','universe']}]),
                   ('apt:adobe-flashplugin?channel=partner',
                    [{'package':'adobe-flashplugin', 'channel': 'partner'}]),
                   ('apt:adobe-flashplugin?channel=$distro-partner',
                    [{'package':'adobe-flashplugin', 'channel': 'hardy-partner'}]),
                   ('apt:linux-restricted-modules-$kernel',
                    [{'package':'linux-restricted-modules-2.6.23-17-generic'}]),
                   ('apt:java?section=multiverse&section=universe',
                    [{'package':'java', 'section':['multiverse','universe']}]),
                   ('apt:java?section=multiverse&section=universe&minver=1.0',
                    [{'package':'java',
                      'section':['multiverse','universe'],
                      'minver': "1.0" }]),
                   ('apt:dpkg:i386', [{ 'package' : 'dpkg:i386',
                                      }]),
                 )

    def test_valid_parse(self):
        for v, e in self.testValues:
            #print("Testing: '%s'" % v)
            result_list = Parser.parse(v, self.mapping)
            for dictionary in e:
                for key in dictionary:
                    self.assertEqual(getattr(result_list[e.index(dictionary)],
                                             key), dictionary[key])

    def test_pkgname_too_long(self):
        self.assertRaises(
            Parser.InvalidUrlException, Parser.parse,
            "apt:" + 100 * "veryverylong")
