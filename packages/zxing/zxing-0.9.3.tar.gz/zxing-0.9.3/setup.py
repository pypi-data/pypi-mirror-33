#!/usr/bin/env python3

from setuptools import setup
from urllib.request import urlretrieve
from urllib.error import URLError
from os import access, path, R_OK
import subprocess as sp
import sys, re

if not sys.version_info[0] == 3:
    sys.exit("Python 2.x is not supported; Python 3.x is required.")

########################################

# Based on this recipe, adapted for Python 3, Git 2.8.x, and PEP-440 version identifiers
#   http://blogs.nopcode.org/brainstorm/2013/05/20/pragmatic-python-versioning-via-setuptools-and-git-tags/
#   https://www.python.org/dev/peps/pep-0440/#version-scheme

# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
version_py = path.join(path.dirname(__file__), 'zxing', 'version.py')

try:
    version_git = sp.check_output(["git", "describe", "--tags", "--dirty=_dirty"]).strip().decode('ascii')
    final, dev, blob, dirty = re.match(r'v?((?:\d+\.)*\d+)(?:-(\d+)-(g[a-z0-9]+))?(_dirty)?', version_git).groups()
    version_pep = final+('.dev%s+%s'%(dev,blob) if dev else '')+(dirty if dirty else '')
except:
    d = {}
    with open(version_py, 'r') as fh:
        exec(fh.read(), d)
        version_pep = d['__version__']
else:
    with open(version_py, 'w') as fh:
        print("# Do not edit this file, versioning is governed by git tags", file=fh)
        print('__version__="%s"' % version_pep, file=fh)

########################################

def download_java_files():
    files = {'java/javase.jar': 'https://repo1.maven.org/maven2/com/google/zxing/javase/3.3.1/javase-3.3.1.jar',
             'java/core.jar': 'https://repo1.maven.org/maven2/com/google/zxing/core/3.3.1/core-3.3.1.jar',
             'java/jcommander.jar': 'https://repo1.maven.org/maven2/com/beust/jcommander/1.72/jcommander-1.72.jar'}

    for fn, url in files.items():
        p = path.join(path.dirname(__file__), 'zxing', fn)
        if access(p, R_OK):
            print("Already have %s." % p)
        else:
            print("Downloading %s from %s ..." % (p, url))
            try:
                urlretrieve(url, p)
            except URLError as e:
                raise SystemExit(*e.args)
    return list(files.keys())

setup(
    name='zxing',
    version=version_pep,
    description="wrapper for zebra crossing (zxing) barcode library",
    long_description="More information: https://github.com/dlenski/python-zxing",
    url="https://github.com/dlenski/python-zxing",
    author='Daniel Lenski',
    author_email='dlenski@gmail.com',
    packages = ['zxing'],
    package_data = {'zxing': download_java_files()},
    entry_points = {'console_scripts': ['zxing=zxing.__main__:main']},
    test_suite = 'nose.collector',
    license='LGPL v3 or later',
)
