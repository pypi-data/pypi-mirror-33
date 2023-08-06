#!/usr/bin/env python3

"""Installateur"""

from setuptools import setup, find_packages
import codecs
import os


def readme():
    """Lecture du README"""
    with codecs.open("README.md", encoding="utf8", errors="replace") as file:
        return file.read()


# Chargement des variables VERSION, COPYRIGHT_YEAR
# Ceci n'est pas fait par un `import pyromaths.version` pour ne pas importer
# des dependances qui ne sont pas encore installees.
with codecs.open("pyromaths/version.py", encoding="utf8", errors="replace") as file:
    exec(compile(file.read(), "version.py", "exec"))

setup(
    name="pyromaths",
    version=VERSION,
    packages=find_packages(exclude=["tests*"]),
    install_requires=["jinja2"],
    include_package_data=True,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description="Create maths exercises in LaTeX and PDF format",
    url="http://www.pyromaths.org",
    download_url="http://www.pyromaths.org/telecharger/",
    license="GPLv2",
    entry_points={"console_scripts": ["pyromaths = pyromaths.__main__:main"]},
    keywords="exercices math latex school",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    long_description=readme(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    project_urls={
        "Documentation": "http://pyromaths.readthedocs.org",
        "Download": "http://www.pyromaths.org/telecharger/",
        "Forum": "http://forum.pyromaths.org",
        "Sources": "https://framagit.org/pyromaths/pyromaths",
        "Tickets": "https://framagit.org/pyromaths/pyromaths/issues",
        "Version en ligne": "http://www.pyromaths.org/enligne/",
    },
)
