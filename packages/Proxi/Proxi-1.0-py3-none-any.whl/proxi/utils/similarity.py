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
Similarity functions for proxi project.
"""

import numpy as np
from scipy import stats
from scipy.spatial import distance
import math


def abs_pcc(x,y):
    """
    Compute absolute Pearson correlation similarity between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        |pcc(x,y)|

    """
    pcc, _ = stats.pearsonr(x, y)
    return math.fabs(pcc)

def abs_spc(x,y):
    """
    Compute absolute Spearman correlation similarity between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        |spearmanr(x,y)|

    """
    spc, _ = stats.spearmanr(x, y, axis=None)
    return math.fabs(spc)

def abs_Kendall(x,y):
    """
    Compute absolute Kendall correlation similarity between two vectors.

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    Returns
    -------
        |kendalltau(x,y)|

    """
    return math.fabs(stats.kendalltau(x,y))

# TODO: how to pass extra parameters for the callable method dist_func?
def distance_to_similarity(x,y, dist_func):
    """
    Convert the distance functions in scipy.spatial.distance into similarity functions

    Parameters
    ----------
    x : array_like, Shape(N,)
        First input vector.
    y : array_like, Shape(N,)
        Second input vector.

    dist_func : collable
        collabel distance function (e.g., any distance function in scipy.spatial.distance)

    Returns
    -------
    similarity between x and y.

    """

    return 1- dist_func(x,y)



