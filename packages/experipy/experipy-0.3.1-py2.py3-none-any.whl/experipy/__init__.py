from __future__ import absolute_import

from . import (
    config,
    exp,
    grammar,
    metrics,
    system,
)


__version__     = "0.3.1"

__title__       = "experipy"
__description__ = "A framework for writing and running Computational Science experiments"
__uri__         = "https://experipy.readthedocs.io"

__author__      = "Adam Howard"
__email__       = "ahoward0920@gmail.com"

__license__     = "BSD 3-clause"
__copyright__   = "Copyright (c) 2016 Adam Howard"


Experiment  = exp.Experiment
Namespace   = config.Namespace

dump_config = config.Namespace.dump_full_config

__all__ = [
    "config",
    "dump_config",
    "exp",
    "grammar",
    "metrics",
    "system",
    "Experiment",
    "Namespace",
]
