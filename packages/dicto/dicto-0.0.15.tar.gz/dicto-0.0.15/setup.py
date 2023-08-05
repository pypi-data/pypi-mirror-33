import os
from setuptools import setup, find_packages


setup(
    name = "dicto",
    version = "0.0.15",
    author = "Cristian Garcia",
    author_email = "cgarcia.e88@gmail.com",
    description = ("An object-like dictionary"),
    license = "MIT",
    keywords = [],
    url = "https://github.com/cgarciae/dicto",
   	packages = find_packages(),
    package_data={
        '': ['LICENCE', 'requirements.txt', 'README.md', 'CHANGELOG.md'],
        'tfinterface': ['README-template.md']
    },
    include_package_data = True,
    install_requires = [
        "PyYAML",
        "xmltodict",
    ]
)
