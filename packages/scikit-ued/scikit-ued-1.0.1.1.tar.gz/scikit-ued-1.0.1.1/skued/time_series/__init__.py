# -*- coding: utf-8 -*-
"""
Time-series analysis
--------------------
This package allows for exploration of time-series data, especially
in the context of ultrafast diffraction.
"""

from .fitting import exponential_decay, biexponential_decay
from .robust import mad
from .nfft_routines import nfft, nfftfreq
from .time_zero import time_shift, time_shifts, register_time_shift, register_time_shifts