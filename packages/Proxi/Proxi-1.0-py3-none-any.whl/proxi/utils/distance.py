# Copyright (c)  2018, Yasser El-Manzalawy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Yasser El-Manzalawy BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Distance functions for proxi project.
"""


import numpy as np
from scipy import stats
import math

def pos_correlation(x,y):
    """
    Compute positive correlation distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if pcc is negative. Otherwise, the distance is 1-pcc(x,y)

    """
    pcc,_ = stats.pearsonr(x,y)
    if pcc < 0:
        pcc = 0
    return 1 - pcc

def neg_correlation(x,y):
    """
    Compute negative correlation distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if pcc is positive. Otherwise, the distance is 1+pcc(x,y)

    """

    pcc,_  = stats.pearsonr(x,y)
    if pcc > 0:
        pcc = 0
    return 1 + pcc  # note that pcc is negative

def abs_correlation(x,y):
    """
    Compute absolute correlation distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1-|pcc(x,y)|

    """
    pcc, _ = stats.pearsonr(x, y)
    return 1 - math.fabs(pcc)



def pos_spearmann(x,y):
    """
    Compute positive spearmann correlation (spc) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if spc is negative. Otherwise, the distance is 1-spc(x,y)

    """

    spc,_ = stats.spearmanr(x,y,axis=None)
    if spc < 0:
        spc = 0
    return 1 - spc

def neg_spearmann(x,y):
    """
    Compute negative spearmann correlation (spc) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if spc is positive. Otherwise, the distance is 1+spc(x,y)

    """

    spc,_ = stats.spearmanr(x,y,axis=None)
    if spc > 0:
        spc = 0
    return 1 + spc

def abs_spearmann(x,y):
    """
    Compute absolute spearmann correlation (spc) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1-|spc(x,y)|

    """

    spc, _ = stats.spearmanr(x, y, axis=None)
    return 1 - math.fabs(spc)


def pos_kendall(x,y):
    """
    Compute positive Kendall correlation (tau) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if tau is negative. Otherwise, the distance is 1-spc(x,y)

    """

    tau,_ = stats.kendalltau(x,y)
    if tau < 0:
        tau = 0
    return 1 - tau

def neg_kendall(x,y):
    """
    Compute negative Kendall correlation (tau) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1 if tau is positive. Otherwise, the distance is 1+tau(x,y)

    """

    tau,_ = stats.kendalltau(x,y)
    if tau > 0:
        tau = 0
    return 1 + tau

def abs_kendall(x,y):
    """
    Compute absolute Kendall correlation (tau) distance between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        1-|tau(x,y)|

    """

    tau, _ = stats.kendalltau(x, y)
    return 1 - math.fabs(tau)



