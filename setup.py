#!/usr/bin/env python3

from distutils.core import setup
from DistUtilsExtra.command import *
import glob
import os
import re

# look/set what version we have
changelog = "debian/changelog"
if os.path.exists(changelog):
    with open(changelog, encoding='utf-8') as fp:
        head = fp.readline()
    match = re.compile(".*\(([0-9.]+)ubuntu.+\).*").match(head)
    if match:
        version = match.group(1)
        with open("AptUrl/Version.py", "w") as fp:
            print('VERSION="{}"'.format(version))

GETTEXT_NAME="apturl"
I18NFILES = []
for filepath in glob.glob("po/mo/*/LC_MESSAGES/*.mo"):
    lang = filepath[len("po/mo/"):]
    targetpath = os.path.dirname(os.path.join("share/locale",lang))
    I18NFILES.append((targetpath, [filepath]))

setup(name='apturl',
      version=version,
      packages=['AptUrl',
                'AptUrl.gtk'],
      scripts=['apturl','apturl-gtk'],
      data_files=[('share/apturl/',
                   ["data/apturl-gtk.ui"]),
                  ('../etc/firefox/pref/',
                   ["data/apturl.js"]),
                  ('share/kde4/services/',
                   ["data/apt.protocol","data/apt+http.protocol"]),
                  ('share/applications/',
                   ["data/apturl.desktop"]),
                 ]+I18NFILES,
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons }
      )
