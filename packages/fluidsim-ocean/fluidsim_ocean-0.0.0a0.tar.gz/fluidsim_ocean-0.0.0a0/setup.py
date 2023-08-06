
from __future__ import print_function

import os
import sys
if sys.version_info[:2] < (3, 5):
    raise RuntimeError("Python version >= 3.6 required.")

from time import time
from runpy import run_path
from datetime import datetime
from distutils.sysconfig import get_config_var

from setuptools import setup, find_packages

from distutils.command.build_ext import build_ext


try:
    from pythran.dist import PythranExtension, build_ext as pythran_build_ext

    use_pythran = True
except ImportError:
    pythran_build_ext = object
    use_pythran = False


class fluidsim_build_ext(build_ext, pythran_build_ext):
    pass


import numpy as np

from config_ocean import monkeypatch_parallel_build, logger

time_start = time()
# config = get_config()

# handle environ (variables) in config
# if 'environ' in config:
#     os.environ.update(config['environ'])

monkeypatch_parallel_build()

logger.info("Running fluidsim_ocean setup.py on platform " + sys.platform)

here = os.path.abspath(os.path.dirname(__file__))


# Get the long description from the relevant file
with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()
lines = long_description.splitlines(True)
long_description = "".join(lines[14:])

# Get the version from the relevant file
d = run_path("fluidsim_ocean/_version.py")
__version__ = d["__version__"]
__about__ = d["__about__"]

print(__about__)

# Get the development status from the version string
if "a" in __version__:
    devstatus = "Development Status :: 3 - Alpha"
elif "b" in __version__:
    devstatus = "Development Status :: 4 - Beta"
else:
    devstatus = "Development Status :: 5 - Production/Stable"

ext_modules = []

define_macros = []

install_requires = ["fluidsim"]


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def make_pythran_extensions(modules):
    exclude_pythran = tuple

    if len(exclude_pythran) > 0:
        logger.info(
            "Pythran files in the packages "
            + str(exclude_pythran)
            + " will not be built."
        )
    develop = sys.argv[-1] == "develop"
    extensions = []
    for mod in modules:
        package = mod.rsplit(".", 1)[0]
        if any(package == excluded for excluded in exclude_pythran):
            continue
        base_file = mod.replace(".", os.path.sep)
        py_file = base_file + ".py"
        # warning: does not work on Windows
        suffix = get_config_var("EXT_SUFFIX") or ".so"
        bin_file = base_file + suffix
        logger.info(
            "make_pythran_extension: {} -> {} ".format(
                py_file, os.path.basename(bin_file)
            )
        )
        if (
            not develop
            or not os.path.exists(bin_file)
            or modification_date(bin_file) < modification_date(py_file)
        ):
            pext = PythranExtension(
                mod, [py_file]  # extra_compile_args=['-O3', '-fopenmp']
            )
            pext.include_dirs.append(np.get_include())
            # bug pythran extension...
            compile_arch = os.getenv("CARCH", "native")
            pext.extra_compile_args.extend(
                ["-O3", "-march={}".format(compile_arch)]
            )
            # pext.extra_link_args.extend(['-fopenmp'])
            extensions.append(pext)
    return extensions


if use_pythran:
    ext_names = []
    for root, dirs, files in os.walk("fluidsim_ocean"):
        for name in files:
            if name.endswith("_pythran.py"):
                path = os.path.join(root, name)
                ext_names.append(path.replace(os.path.sep, ".").split(".py")[0])

    ext_modules += make_pythran_extensions(ext_names)

console_scripts = [
    # 'fluidsim = fluidsim.util.console.__main__:run',
]


setup(
    name="fluidsim_ocean",
    version=__version__,
    description=("Fluidsim solvers for oceanic studies."),
    long_description=long_description,
    keywords="Fluid dynamics, research",
    author="Pierre Augier",
    author_email="pierre.augier@univ-grenoble-alpes.fr",
    url="https://bitbucket.org/fluiddyn/fluidsim_ocean",
    license="CeCILL",
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        devstatus,
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        # actually CeCILL License (GPL compatible license for French laws)
        #
        # Specify the Python versions you support here. In particular,
        # ensure that you indicate whether you support Python 2,
        # Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
    packages=find_packages(exclude=["doc"]),
    install_requires=install_requires,
    extras_require=dict(doc=["Sphinx>=1.1", "numpydoc"], parallel=["mpi4py"]),
    cmdclass={"build_ext": fluidsim_build_ext},
    ext_modules=ext_modules,
    entry_points={"console_scripts": console_scripts},
)

logger.info("Setup completed in {:.3f} seconds.".format(time() - time_start))
