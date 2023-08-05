"""Setup script for hbd"""

import re
from setuptools import setup

# Extract version number from source code
with open('hbd.py', 'r') as f:
    source_code = f.read()
    version_regex = re.compile(r'''^\s*__version__\s*=\s*['"](\d.*)['"]''', re.MULTILINE)
    VERSION = version_regex.search(source_code).group(1)

with open('README.md', 'r') as f:
    README_TEXT = f.read()

setup(
    name='hbd',
    description='API and CLI for Humble Bundle downloads.',
    long_description=README_TEXT,
    url="https://gitlab.com/BitLooter/hbd",
    author="David Powell",
    author_email="BitLooter@users.noreply.github.com",
    version=VERSION,
    py_modules=['hbd', 'cli'],
    install_requires=[
        'appdirs',
        'attrs',
        'click',
        'colorama',
        'requests',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'hbd=cli:main'
        ]
    },
    license='LGPL3'
)
