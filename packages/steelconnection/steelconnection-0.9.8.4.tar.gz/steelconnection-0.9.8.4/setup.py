import re
import setuptools

from steelconnection.__version__ import __author__, __author_email__
from steelconnection.__version__ import __copyright__, __description__
from steelconnection.__version__ import __license__, __title__
from steelconnection.__version__ import __url__, __version__


keywords = ['SteelConnect', 'REST', 'API', 'Riverbed', 'Grelleum']

classifiers=[
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
]

with open('README.md', 'rt') as f:
    readme = f.read()

long_description = re.sub(
    r'##### version \d+\.[\d\.]+',
    '##### version ' + __version__,
    readme,
)

# if readme != long_description:
#     with open('README.md', 'wt') as f:
#         f.write(long_description)

packages = setuptools.find_packages()

setuptools.setup(
    name=__title__,
    install_requires='requests>=2.12.1',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=__url__,
    keywords=keywords,
    packages=packages,
    license=__license__,
    classifiers=classifiers,
)
    # install_requires=['requests>=2.12.1'],
