"""Chemin de quelques répertoires propres à Pyromaths."""

import os

import pkg_resources

DATADIR = pkg_resources.resource_filename("pyromaths", "data")
EXODIR = os.path.join(DATADIR, "exercices")
LOCALEDIR = os.path.join(DATADIR, "locale")
