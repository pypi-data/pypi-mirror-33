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
Pre-processing methods for proxi project.
"""


import numpy as np
import pandas as pd


def select_top_OTUs (data, score_function, threshold, OTUs_column):
    """
    Filter OTUs using a scoring function and return top k OTUs or OTUs with scores greater than a threshold score.

    Parameters
    ----------
    data : DataFrame
        Input data as a pandas DataFrame object. Each row is an OTU and each column is a sample

    score_function : collable function
        Unsupervised scoring function (e.g., variance or percentage of non-zeros) of each OTU.

    threshold : float
        if threshold > 1, return top threshold OTUs. Otherwise, return OTUs with score > threshold.

    OTU_column : string
        Name of the DataFrame column that contains the OTUs IDs (i.e., nodes IDs).

    Returns
    -------
        dataframe with selected OTUs
    """
    OTUs_name = data[OTUs_column].values

    X = data.drop([OTUs_column], axis=1).values
    n_OTUs, n_samples = np.shape(X)
    _scores = np.zeros(n_OTUs)
    for i in range(n_OTUs):
        _scores[i] = score_function(X[i,:])

    if threshold > 1:
        indices = np.argsort(_scores)[::-1]
        selected_indices = indices[0:threshold]

    else:
        selected_indices = [x for x in range(n_OTUs) if _scores[x]>= threshold]

    # keep selected OTUs only
    df = data[data[OTUs_column].isin(OTUs_name[selected_indices])]

    return df

def filter_OTUs_by_name(data, OTUs_to_keep, OTUs_column):
    """
    Keeps only the OTUs in OTUs_to_keep list.

    Parameters
    ----------
    data : DataFrame
        Input data as a pandas DataFrame object. Each row is an OTU and each column is a sample

    OTUs_to_keep : list
        List of OTUs ID to select from the input dataframe.

    OTU_column : string
        Name of the DataFrame column that contains the OTUs IDs (i.e., nodes IDs).

    Returns
    -------
    A dataframe derived from the input data by keeping only rows with specified OTUs IDs.
    """
    return data[data[OTUs_column].isin(OTUs_to_keep)]


def get_variance(x):
    """
    Compute the variance of an input vector x.
    Variance is the average of the squared deviations from the meanvar = mean(abs(x - x.mean())**2)

    Parameters
    ----------
    x : array_like, Shape(N,)
        Input 1-D array.

    Returns
    -------
    The variance of x.
    """
    return np.var(x)  # variance of the flattened array



def get_non_zero_percentage(x):
    """
    The fraction of non-zero values in a 1-D array x.

    Parameters
    ----------
    x : array_like, Shape(N,)
        Input 1-D array.

    Returns
    -------
    The percentage of non-zero elements in x.
    """
    return np.count_nonzero(x)/np.size(x)

def get_MAD(x):
    """
    MAD is defined as the median of the absolute deviations from the data's median:

    Parameters
    ----------
    x : array_like, Shape(N,)
        Input 1-D array.

    Returns
    -------
    The median of the absolute deviations (MAD) of x.
    """
    return np.median(np.fabs(x-np.median(x)))




