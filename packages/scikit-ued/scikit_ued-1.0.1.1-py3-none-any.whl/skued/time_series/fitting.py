# -*- coding: utf-8 -*-
"""
Convenience functions for fitting time-series.
"""

import numpy as np

# TODO: triexponential
#       oscillation after onset
#       Test against negative amplitudes or time-constants?

def exponential_decay(time, tzero, amp, tconst, offset = 0):
    """
    Exponential decay curve with onset. Equivalent to the following function:

    .. math::

        I(t) =
        \\begin{cases} 
            I_0 + O &\\text{if } t < t_0 \\\\
            I_0 e^{-(t - t_0)/\\tau} + O &\\text{if } t \ge t_0
        \\end{cases}

    This functions is expected to be used in conjunction with 
    ``scipy.optimize.curve_fit`` or similar fitting routines.

    Parameters
    ----------
    time : `~numpy.ndarray`, shape(N,)
        Time values array [ps].
    tzero : float
        Time-zero :math:`t_0` [ps]. Exponential decay happens for :math:`t > t_0`.
    amp : float
        Initial amplitude :math:`I_0`.
    tconst : float
        Decay time-constant :math:`\\tau` [ps].
    offset : float, optional
        Constant amplitude offset :math:`O`.

    Returns
    -------
    exp_decay : `~numpy.ndarray`, shape (N,)
        Exponential decay curve.
    
    See also
    --------
    biexponential_decay : bi-exponential decay
    """
    arr = np.full_like(time, amp + offset, dtype = np.float)
    arr[time > tzero] = amp * np.exp(-(time[time > tzero] - tzero)/tconst) + offset
    return arr

def biexponential_decay(time, tzero, amp1, amp2, tconst1, tconst2, offset = 0):
    """
    Bi-exponential decay curve with onset. Equivalent to the following function:

    .. math::

        I(t) =
        \\begin{cases} 
            I_1 + I_2 + O &\\text{if } t < t_0 \\\\
            I_1 e^{-(t - t_0)/\\tau_1} + I_2 e^{-(t - t_0)/\\tau_2} + O &\\text{if } t \ge t_0
        \\end{cases}

    This functions is expected to be used in conjunction with 
    ``scipy.optimize.curve_fit`` or similar fitting routines.

    Parameters
    ----------
    time : `~numpy.ndarray`, shape(N,)
        Time values array [ps].
    tzero : float
        Time-zero :math:`t_0` [ps]. Exponential decay happens for :math:`t > t_0`.
    amp1 : float
        Initial amplitude :math:`I_1`.
    amp2 : float
        Initial amplitude :math:`I_2`.
    tconst1 : float
        Decay time-constant :math:`\\tau_1` [ps].
    tconst2 : float
        Decay time-constant :math:`\\tau_2` [ps].
    offset : float, optional
        Constant amplitude offset :math:`O`.

    Returns
    -------
    biexp_decay : `~numpy.ndarray`, shape (N,)
        Biexponential decay curve.
    
    See also
    --------
    exponential_decay : single-exponential decay
    """
    arr = np.full_like(time, amp1 + amp2, dtype = np.float)
    after_tzero = time > tzero
    arr[after_tzero] = amp1 * np.exp(-(time[time > tzero] - tzero)/tconst1)
    arr[after_tzero] += amp2 * np.exp(-(time[time > tzero] - tzero)/tconst2)
    return arr + offset