import os
import re
import sys
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'src', 'abi', 'tools', 'generateuserinterface.py')) as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

try:
    import PySide
    have_pyside = True
except ImportError:
    have_pyside = False

if have_pyside or sys.version_info < (3, 5):
    reqs = ['PySide']
else:
    reqs = ['PySide2']

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="abi.tools.uigenerator",
    version=version,
    author="Auckland Bioengineering Institute",
    author_email="h.sorby@auckland.ac.nz",
    description="Python client for generating Python user interface descriptions.",
    long_description=long_description,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    install_requires=reqs,
    entry_points={
        'gui_scripts': [
            'uigenerator=abi.tools.generateuserinterface:main',
        ]
    },
    license="",
    keywords="abi user interface generator",
    url="https://github.com/ABI-Software/abi.tools.uigenerator",
    download_url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
