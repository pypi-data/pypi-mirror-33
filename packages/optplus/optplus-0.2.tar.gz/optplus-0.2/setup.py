#!/usr/bin/env python

"""optplus: additional options for optparse

I hope these can be contributed to optparse someday.
"""

from __future__ import absolute_import
__version__ = "0.2"

# Copyright 2009 Michael M. Hoffman <mmh1@washington.edu>

from setuptools import find_packages, setup

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

url = "http://noble.gs.washington.edu/~mmh1/software/%s/" % name.lower()
download_url = "%s%s-%s.tar.gz" % (url, name, __version__)

classifiers = ["Natural Language :: English",
               "Programming Language :: Python"]

if __name__ == "__main__":
    setup(name=name,
          version=__version__,
          description=short_description,
          author="Michael Hoffman",
          author_email="mmh1@washington.edu",
          url=url,
          download_url=download_url,
          classifiers=classifiers,
          long_description=long_description,
          zip_safe=True,

          # XXX: this should be based off of __file__ instead
          packages=find_packages("."),
          )
