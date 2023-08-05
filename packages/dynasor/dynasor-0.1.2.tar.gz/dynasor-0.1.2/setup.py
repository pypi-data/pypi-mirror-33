#!/usr/bin/env python

import re
import sys

from config import (extra_compile_args, extra_link_args,
                    local_compiler, local_link_shared, local_linker)
try:
    from setuptools import setup, Extension
except ImportError:
    print('setuptools not found; falling back to distutils')
    from distutils.core import setup
    from distutils.extension import Extension
from distutils.sysconfig import get_config_vars


if sys.version_info < (3, 5, 0, 'final', 0):
    raise SystemExit('Python 3.5 or later is required!')

with open('README.rst', encoding='utf-8') as fd:
    long_description = fd.read()


if local_compiler is not None:
    # Kludge: Force compiler of choice for building _rho_j_k.c.
    # _rho_j_k.c only contains a plain c-function with no python-
    # dependencies at all. Hence, just blatantly set simple
    # compiler, linker and flags (inspired by GPAW setup.py).

    config_vars = get_config_vars()
    for key in ['BASECFLAGS', 'CFLAGS', 'OPT', 'PY_CFLAGS',
                'CCSHARED', 'CFLAGSFORSHARED', 'LINKFORSHARED',
                'LIBS', 'SHLIBS']:
        config_vars[key] = ''

    config_vars['CC'] = local_compiler
    config_vars['LDSHARED'] = ' '.join([local_linker] + local_link_shared)

rho_j_k_d_ext = Extension('dsf._rho_j_k_d',
                          sources=['src/_rho_j_k.c'],
                          define_macros=[('RHOPREC', 'double')],
                          extra_compile_args=extra_compile_args,
                          extra_link_args=extra_link_args,
                          )

rho_j_k_s_ext = Extension('dsf._rho_j_k_s',
                          sources=['src/_rho_j_k.c'],
                          define_macros=[('RHOPREC', 'float')],
                          extra_compile_args=extra_compile_args,
                          extra_link_args=extra_link_args,
                          )


with open('dsf/__init__.py') as fd:
    lines = '\n'.join(fd.readlines())
version = re.search("__version__ = '(.*)'", lines).group(1)
maintainer = re.search("__maintainer__ = '(.*)'", lines).group(1)
maintainer_email = re.search("__maintainer_email__ = '(.*)'", lines).group(1)
url = re.search("__url__ = '(.*)'", lines).group(1)
license = re.search("__license__ = '(.*)'", lines).group(1)
description = re.search("__description__ = '(.*)'", lines).group(1)

# PyPI name
name = 'dynasor'
# Linux-distributions may want to change the name:
if 0:
    name = 'python-dynasor'

setup(name=name,
      version=version,
      description=description,
      long_description=long_description,
      url=url,
      maintainer=maintainer,
      maintainer_email=maintainer_email,
      packages=['dsf', 'dsf/trajectory_reader'],
      include_package_data=True,
      ext_modules=[rho_j_k_d_ext, rho_j_k_s_ext],
      scripts=['dynasor'],
      # data_files=[('man/man1', ['dynasor.1'])],
      install_requires=['numpy'],
      license='GPL2+',
      platforms=['unix'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Programming Language :: C',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Topic :: Scientific/Engineering :: Physics'])
