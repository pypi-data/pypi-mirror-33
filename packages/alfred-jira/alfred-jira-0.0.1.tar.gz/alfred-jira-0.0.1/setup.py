import json
from setuptools import setup

try:
    with open('README.MD') as readme_file:
        README = readme_file.read()
except FileNotFoundError:
    README = ""


try:
    with open("Pipfile.lock") as pipfile:
        JSON_PIPFILE = json.load(pipfile)
        INSTALL_REQUIRES = []
        for key, value in dict(JSON_PIPFILE["default"]).items():
            INSTALL_REQUIRES.append("{}{}".format(key, value["version"]))
except FileNotFoundError:
    INSTALL_REQUIRES = []

VERSION = '0.0.1'

setup(
    name='alfred-jira',
    packages=['alfred_jira'],
    version=VERSION,
    description='',
    long_description=README,
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': ['alfred-jira=alfred_jira:cli'],
    },
    author_name='Romain Moreau',
    author_email='moreau.romain83@gmail.com',
    url='https://github.com/Varkal/alfred-jira',
    download_url='https://github.com/Varkal/alfred-jira/archive/{}.tar.gz'.format(VERSION),
    keywords=['alfred-jira'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
