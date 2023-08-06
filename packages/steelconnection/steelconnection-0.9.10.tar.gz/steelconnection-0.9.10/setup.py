from setuptools import setup
import re


name = 'steelconnection'
copyright = 'Copyright 2018 Greg Mueller'

variables = {
    'description': 'Simplify access to the Riverbed SteelConnect REST API.',
    'version': '0.9.10',
    'author': 'Greg Mueller',
    'author_email': 'steelconnection@grelleum.com',
    'license': 'MIT',
    'url': 'https://github.com/grelleum/SteelConnection',
    'long_description_content_type': 'text/markdown',
    'install_requires': ['requests>=2.12.1'],
    'keywords': ['SteelConnect', 'REST', 'API', 'Riverbed', 'Grelleum'],
    'packages': ['steelconnection'],
    'classifiers': [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
}



# __title__ = 'steelconnection'
# __description__ = 'Simplify access to the Riverbed SteelConnect REST API.'
# __version__ = '0.9.10'
# __author__ = 'Greg Mueller'
# __author_email__ = 'steelconnection@grelleum.com'
# __copyright__ = 'Copyright 2018 Greg Mueller'
# __license__ = 'MIT'
# __url__ = 'https://github.com/grelleum/SteelConnection'

# content_type = 'text/markdown'
# install_requires = ['requests>=2.12.1']
# keywords = ['SteelConnect', 'REST', 'API', 'Riverbed', 'Grelleum']
# packages = ['steelconnection']
# classifiers = [
#     'Programming Language :: Python :: 2',
#     'Programming Language :: Python :: 2.7',
#     'Programming Language :: Python :: 3',
#     'Programming Language :: Python :: 3.4',
#     'Programming Language :: Python :: 3.5',
#     'Programming Language :: Python :: 3.6',
#     'Programming Language :: Python :: 3.7',
#     'License :: OSI Approved :: MIT License',
#     'Operating System :: OS Independent'
# ]



export_variables = {k: variables[k] for k in variables}
export_variables['title'] = name
export_variables['copyright'] = copyright
keys = [
    'title', 'description', 'version', 'author',
    'author_email', 'copyright', 'license', 'url',
]
text = "__{0}__ = '{1}'\n"
with open(name + '/__version__.py', 'wt') as f:
    for key in keys:
        f.write(text.format(key, export_variables[key]))


# with open(__title__ + '/__version__.py', 'wt') as f:
#     text = "{0} = '{1}'\n"
#     f.write(text.format('__title__', __title__))
#     f.write(text.format('__description__', __description__))
#     f.write(text.format('__version__', __version__))
#     f.write(text.format('__author__', __author__))
#     f.write(text.format('__author_email__', __author_email__))
#     f.write(text.format('__copyright__', __copyright__))
#     f.write(text.format('__license__', __license__))
#     f.write(text.format('__url__', __url__))


# with open('README.md', 'rt') as f:
#     readme = f.read()
# long_description = re.sub(
#     r'##### version \d+\.[\d\.]+[a-z]?',
#     '##### version ' + __version__,
#     readme,
# )
# with open('README.md', 'wt') as f:
#     f.write(long_description)

# print('VERSION:', __version__)


with open('README.md', 'rt') as f:
    readme = f.read()
long_description = re.sub(
    r'##### version \d+\.[\d\.]+[a-z]?',
    '##### version ' + variables['version'],
    readme,
)
with open('README.md', 'wt') as f:
    f.write(long_description)

print('VERSION:', variables['version'])
variables['long_description'] = long_description
setup(name=name, **variables)



# setup(
#     name=__title__,
#     install_requires=install_requires,
#     version=__version__,
#     author=__author__,
#     author_email=__author_email__,
#     description=__description__,
#     long_description=long_description,
#     long_description_content_type=content_type,
#     url=__url__,
#     keywords=keywords,
#     packages=packages,
#     license=__license__,
#     classifiers=classifiers,
# )
