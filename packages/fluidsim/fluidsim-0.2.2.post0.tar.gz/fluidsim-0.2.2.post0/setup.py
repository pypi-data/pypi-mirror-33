
from __future__ import print_function

import os
import sys
from time import time
from runpy import run_path
from datetime import datetime
from distutils.sysconfig import get_config_var

from setuptools import setup, find_packages

try:
    from Cython.Distutils.extension import Extension
    from Cython.Distutils import build_ext
    from Cython.Compiler import Options as CythonOptions
    has_cython = True
    ext_source = 'pyx'
except ImportError:
    from setuptools import Extension
    from distutils.command.build_ext import build_ext
    has_cython = False
    ext_source = 'c'

try:
    from pythran.dist import PythranExtension
    use_pythran = True
except ImportError:
    use_pythran = False

import numpy as np

from config import (
    MPI4PY, FFTW3, monkeypatch_parallel_build, get_config, logger)

if use_pythran:
    try:
        from pythran.dist import PythranBuildExt

        class fluidsim_build_ext(build_ext, PythranBuildExt):
            pass
    except ImportError:
        fluidsim_build_ext = build_ext
else:
    fluidsim_build_ext = build_ext


time_start = time()
config = get_config()

# handle environ (variables) in config
if 'environ' in config:
    os.environ.update(config['environ'])

monkeypatch_parallel_build()

logger.info('Running fluidsim setup.py on platform ' + sys.platform)

here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[0:2] < (3, 2):
    raise RuntimeError("Python version 2.7 or >= 3.2 required.")

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()
lines = long_description.splitlines(True)
long_description = ''.join(lines[14:])

# Get the version from the relevant file
d = run_path('fluidsim/_version.py')
__version__ = d['__version__']
__about__ = d['__about__']

print(__about__)

# Get the development status from the version string
if 'a' in __version__:
    devstatus = 'Development Status :: 3 - Alpha'
elif 'b' in __version__:
    devstatus = 'Development Status :: 4 - Beta'
else:
    devstatus = 'Development Status :: 5 - Production/Stable'

ext_modules = []

logger.info('Importing mpi4py: {}'.format(MPI4PY))

define_macros = []
if has_cython and os.getenv('TOXENV') is not None:
    cython_defaults = CythonOptions.get_directive_defaults()
    cython_defaults['linetrace'] = True
    define_macros.append(('CYTHON_TRACE_NOGIL', '1'))

path_sources = 'fluidsim/base/time_stepping'
ext_cyfunc = Extension(
    'fluidsim.base.time_stepping.pseudo_spect_cy',
    include_dirs=[
        path_sources,
        np.get_include()],
    libraries=['m'],
    library_dirs=[],
    sources=[path_sources + '/pseudo_spect_cy.' + ext_source],
    define_macros=define_macros)

ext_modules.append(ext_cyfunc)

logger.info('The following extensions could be built if necessary:\n' +
      ''.join([ext.name + '\n' for ext in ext_modules]))


install_requires = ['fluiddyn >= 0.2.3', 'future >= 0.16',
                    'h5py', 'h5netcdf']

if FFTW3:
    install_requires += ['pyfftw >= 0.10.4', 'fluidfft >= 0.2.4']


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def make_pythran_extensions(modules):
    exclude_pythran = tuple(
        key for key, value in config['exclude_pythran'].items()
        if value)
    if len(exclude_pythran) > 0:
        logger.info('Pythran files in the packages ' + str(exclude_pythran) +
                    ' will not be built.')
    develop = sys.argv[-1] == 'develop'
    extensions = []
    for mod in modules:
        package = mod.rsplit('.', 1)[0]
        if any(package == excluded for excluded in exclude_pythran):
            continue
        base_file = mod.replace('.', os.path.sep)
        py_file = base_file + '.py'
        # warning: does not work on Windows
        suffix = get_config_var('EXT_SUFFIX') or '.so'
        bin_file = base_file + suffix
        logger.info('make_pythran_extension: {} -> {} '.format(
            py_file, os.path.basename(bin_file)))
        if not develop or not os.path.exists(bin_file) or \
           modification_date(bin_file) < modification_date(py_file):
            pext = PythranExtension(
                mod, [py_file], extra_compile_args=['-O3']
            )
            pext.include_dirs.append(np.get_include())
            # bug pythran extension...
            compile_arch = os.getenv('CARCH', 'native')
            pext.extra_compile_args.extend(['-O3',
                                            '-march={}'.format(compile_arch)])
            # pext.extra_link_args.extend(['-fopenmp'])
            extensions.append(pext)
    return extensions


if use_pythran:
    ext_names = []
    for root, dirs, files in os.walk('fluidsim'):
        for name in files:
            if name.endswith('_pythran.py'):
                path = os.path.join(root, name)
                ext_names.append(
                    path.replace(os.path.sep, '.').split('.py')[0])

    ext_modules += make_pythran_extensions(ext_names)

console_scripts = [
    'fluidsim = fluidsim.util.console.__main__:run',
    'fluidsim-test = fluidsim.util.testing:run',
    'fluidsim-create-xml-description = fluidsim.base.output:run']

for command in ['profile', 'bench', 'bench-analysis']:
    console_scripts.append(
        'fluidsim-' + command +
        ' = fluidsim.util.console.__main__:run_' + command.replace('-', '_'))


setup(name='fluidsim',
      version=__version__,
      description=('Framework for studying fluid dynamics with simulations.'),
      long_description=long_description,
      keywords='Fluid dynamics, research',
      author='Pierre Augier',
      author_email='pierre.augier@legi.cnrs.fr',
      url='https://bitbucket.org/fluiddyn/fluidsim',
      license='CeCILL',
      classifiers=[
          # How mature is this project? Common values are
          # 3 - Alpha
          # 4 - Beta
          # 5 - Production/Stable
          devstatus,
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          # actually CeCILL License (GPL compatible license for French laws)
          #
          # Specify the Python versions you support here. In particular,
          # ensure that you indicate whether you support Python 2,
          # Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Cython',
          'Programming Language :: C',
      ],
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      packages=find_packages(exclude=['doc', 'examples']),
      install_requires=install_requires,
      extras_require=dict(
          doc=['Sphinx>=1.1', 'numpydoc'],
          parallel=['mpi4py']),
      cmdclass={"build_ext": fluidsim_build_ext},
      ext_modules=ext_modules,
      entry_points={'console_scripts': console_scripts})

logger.info('Setup completed in {:.3f} seconds.'.format(time() - time_start))
