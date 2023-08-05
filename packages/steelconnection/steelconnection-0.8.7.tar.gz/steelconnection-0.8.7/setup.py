import re
import setuptools

import steelconnection.version
version = steelconnection.version.__version__

name = 'steelconnection'
description = 'Simplify REST API access to Riverbed SteelConnect.'
keywords = ['SteelConnect', 'REST', 'API', 'Riverbed', 'Grelleum']
url = 'https://github.com/grelleum/SteelConnection'
author = 'Greg Mueller'
author_email = 'steelconnection@grelleum.com'
base_url = 'https://github.com/grelleum/SteelConnection/archive/'

classifiers=(
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
)

with open('README.md', 'rt') as f:
    long_description = f.read()

download_url = base_url + version + '.tar.gz'

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=url,
    download_url=download_url,
    keywords = keywords,
    packages=setuptools.find_packages(),
    classifiers=classifiers
)