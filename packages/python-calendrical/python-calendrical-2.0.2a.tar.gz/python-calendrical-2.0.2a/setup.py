#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name="python-calendrical",
      version="2.0.2a",
      license = 'BSD 2-Clause',
      description="Calendrical calculation module",
      author="Tadayoshi Funaba",
      author_email="tadf@funaba.org",
      url="http://www.funaba.org/",
      download_url="http://www.funaba.org/archives/python-calendrical-2.0.2.tar.gz",
      ext_modules = [Extension('calendrical',
                               ['ext/calendrical/calendricalmodule.c',
                                'ext/calendrical/calendrical.c',
                                'ext/calendrical/calendrical2.c',
                                'ext/calendrical/qref.c'],
                               include_dirs=['ext/calendrical'])],
      package_dir = {'': 'lib'},
      py_modules = ['calendar2'])
