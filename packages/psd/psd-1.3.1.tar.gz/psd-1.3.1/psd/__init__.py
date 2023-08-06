#!/usr/bin/env python3
"""
Import, compute and plot Power Spectral Densities.

Use this tool to quickly compute, or plot PSDs from data contained
in one or multiple files, using parametrized Welch method. Quick
conversion tool is included to allow quick format conversion.

Jean-Baptiste Bayle, APC/CNRS/CNES, 28/06/2018.
"""

from .psd import Series
from .psd import SpectralEstimator
