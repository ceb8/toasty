# This file and its tests is adapted from Glue (http://glueviz.org).

# Copyright (c) 2013, Glue Developers
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# * Neither the name of the Glue project nor the names of its contributors may be
#   used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np


def norm(x, vmin, vmax):
    """
    Linearly scale data between [vmin, vmax] to [0, 1]. Clip outliers
    """
    result = (x - 1.0 * vmin)
    result = np.divide(result, vmax - vmin, out=result)
    result = np.clip(result, 0, 1, out=result)
    return result


def cscale(x, bias, contrast):
    """
    Apply bias and contrast scaling. Overwrite input

    Parameters
    ----------
    x : array
      Values between 0 and 1
    bias : float
    contrast : float

    Returns
    -------
    The input x, scaled inplace
    """
    x = np.subtract(x, bias, out=x)
    x = np.multiply(x, contrast, out=x)
    x = np.add(x, 0.5, out=x)
    x = np.clip(x, 0, 1, out=x)
    return x


def linear_warp(x, vmin, vmax, bias, contrast):
    return cscale(norm(x, vmin, vmax), bias, contrast)


def log_warp(x, vmin, vmax, bias, contrast, exp=1000.0):
    black = x < vmin
    x = norm(x, vmin, vmax)
    x = np.multiply(exp, x, out=x)
    # sidestep numpy bug that masks log(1)
    # when out is provided
    x = np.add(x, 1.001, out=x)
    x = np.log(x, out=x)
    x = np.divide(x, np.log(exp + 1.0), out=x)
    x = cscale(x, bias, contrast)
    return x


def pow_warp(x, vmin, vmax, bias, contrast, exp=1000.0):
    x = norm(x, vmin, vmax)
    x = np.power(exp, x, out=x)
    x = np.subtract(x, 1, out=x)
    x = np.divide(x, exp - 1)
    x = cscale(x, bias, contrast)
    return x


def sqrt_warp(x, vmin, vmax, bias, contrast):
    x = norm(x, vmin, vmax)
    x = np.sqrt(x, out=x)
    x = cscale(x, bias, contrast)
    return x


def squared_warp(x, vmin, vmax, bias, contrast):
    x = norm(x, vmin, vmax)
    x = np.power(x, 2, out=x)
    x = cscale(x, bias, contrast)
    return x


def asinh_warp(x, vmin, vmax, bias, contrast):
    x = norm(x, vmin, vmax)
    x = np.divide(np.arcsinh(np.multiply(x, 10, out=x), out=x), 3, out=x)
    x = cscale(x, bias, contrast)
    return x


def sinh_warp(x, vmin, vmax, bias, contrast):
    x = norm(x, vmin, vmax)
    x = np.divide(np.sinh(np.multiply(x, 3, out=x), out=x), 10, out=x)
    x = cscale(x, bias, contrast)
    return x

warpers = dict(linear=linear_warp,
               log=log_warp,
               sqrt=sqrt_warp,
               power=pow_warp,
               squared=squared_warp,
               arcsinh=asinh_warp,
               sinh=sinh_warp)

def normalize(value, vmin, vmax, bias=.5, contrast=1, stretch='linear'):
    """Normalize data, by scaling between vmin and vmax, with given bias, contrast, and stretch.

    Parameters
    ----------
    value: array
      values to be normalized
    vmin,vmax: float
      minimum and maximum values for the normalized output
    bias: float (default 0.5)
      bias scaling to be applied during normalization 
    contrast: float (default 1)
      contrast scaling to be applied during normalization
    stretch: string (default 'linear')
      stretch to apply to the data
      valid values are: linear,log,sqrt,power,squared,arcsinh,sinh

    Returns
    -------
    The normalized data array
    """
    
    inverted = vmax <= vmin

    hi, lo = max(vmin, vmax), min(vmin, vmax)

    if stretch not in warpers:
        raise ValueError("Invalid stretch option %s. Valid options are %s" %
                         (stretch, warpers.keys()))

    warp = warpers[stretch]
    result = warp(value, lo, hi, bias, contrast)

    if inverted:
        result = np.subtract(1, result, out=result)

    result = np.multiply(255, result, out=result)
    result = np.clip(result, 0, 255, out=result)
    return result.astype(np.uint8)
