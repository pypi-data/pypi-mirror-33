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
Construct a graph using a pairwise similarity metric (e.g. PCC).
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from proxi.utils.similarity import abs_pcc
from proxi.utils.misc import save_graph, save_weighted_graph

__all__ = ['create_graph_using_pairwise_metric']


def create_graph_using_pairwise_metric(data, similarity_metric, threshold, is_symmetric=True, OTU_column=None,
                                       is_normalize_samples=True, is_standardize_otus=True, is_weighted=False):
    """
    Construct a graph using a pairwise similarity metric.

    Parameters
    ----------
    data : DataFrame
        Input data as pandas DataFrame object. Each row is an OTU and each column is a sample.

    similarity_metric : collable similarity function
        A collable function for computing the similarity between two vectors.

    threshold : float
        Minimum similarity score between two vectors required for having an edgle between their corresponding nodes.

    is_symmetric : bool, optional, default=True
        Set this parameter to False if the similarity function is not symmetric.

    OTU_column : string, optional, default = None
        Name of the DataFrame column that contains the OTUs IDs (i.e., nodes IDs).
        If OTU_column is None, the first column in the dataframe is treated as the OTU_column.


    is_normalize_samples : bool, optional, default = True
        whether to normalize each sample (i.e., column in the input data).

    is_standardize_otus : bool, optional, default = True
        whether to standardize each OTU (i.e., row in the input data)

    is_weighted : bool, optional, default = False
        whether to compute weighted graph. Default is unweighted.


    Returns
    -------
        nodes_IDs : array_like
            list of nodes.
        A : array_like, Shape(N,N)
            Adjacency matrix of the constructed graph.
        W : array_like, Shape(N,N)
            Weight matrics.

    Examples
    --------
    >>> df = pd.read_csv(in_file)
    >>> nodes, a, weights = create_graph_using_pairwise_metric(df, similarity_metric=abs_pcc,
    >>>                            threshold=0.5, is_weighted=True)
    >>> # save unweighted graph in graphml format
    >>> save_graph(a, nodes, out_file)
    >>> # save weighted graph in graphml format
    >>> save_weighted_graph(a, nodes, weights, out_file2)

    TODO
    ----
    Add Notebook example with cytoscape visualized graphs.
    """

    if OTU_column is None:
        node_id_column = data.columns[0]
    else:
        node_id_column = OTU_column

    nodes_IDs = data[node_id_column].values

    X = data.drop([node_id_column], axis=1).values
    print('Shape of original data is {}'.format(np.shape(X)))

    num_nodes, num_samples = np.shape(X)

    # normalize each sample (column) by the sum
    if is_normalize_samples:
        X = normalize(X, norm='l1', axis=0)

    if is_standardize_otus:
        X = StandardScaler().fit_transform(X.T, None).T  # standardize OTUs (rows)

    # Compute similarity matrix
    S = np.zeros(shape=(num_nodes, num_nodes))
    if is_symmetric:  # sim(x,y) = sim(y,x)
        for i in range(num_nodes):
            for j in range(num_nodes):
                if j >= i:
                    break
                S[i, j] = similarity_metric(X[i, :], X[j, :])
                S[j, i] = S[i, j]
    else:
        for i in range(num_nodes):
            for j in range(num_nodes):
                if j == i:
                    break
                S[i, j] = similarity_metric(X[i, :], X[j, :])

    edges_indeces = np.where(S >= threshold)

    A = np.zeros_like(S)
    A[edges_indeces] = 1.

    W = None
    if is_weighted:
        W = np.multiply(A, S)

    return nodes_IDs, A, W
