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
Warrper for using sklearng kNN Graph (KNNG) construction method (see  http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.kneighbors_graph.html).
"""

import numpy as np
import pandas as pd

from sklearn.preprocessing import normalize, StandardScaler
from sklearn.neighbors import kneighbors_graph

from proxi.utils.misc import save_graph

__all__ = ['get_knn_graph']


def get_knn_graph(data, k, metric='correlation', p=2, metric_params=None, OTU_column=None, is_undirected=True,
                  is_normalize_samples=True, is_standardize_otus=True):
    """Compute the (directed/undirected) graph of k-Neighbors for points in the input data.
    The kNN-graph is constructed using sklearn method, sklearn.neighbors.kneighbors_graph.

    Parameters
    ----------
    data : DataFrame
        Input data as pandas DataFrame object. Each row is an OTU and each column is a sample

    k : int
        Number of neighbors for each node

    metric : string or callable, default 'correlation'
        metric to use for distance computation. Any metric from scikit-learn
        or scipy.spatial.distance can be used.

        If metric is a callable function, it is called on each
        pair of instances (rows) and the resulting value recorded. The callable
        should take two arrays as input and return one value indicating the
        distance between them.

        Valid values for metric are:

        - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
          'manhattan']

        - from scipy.spatial.distance: ['braycurtis', 'canberra', 'chebyshev',
          'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
          'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto',
          'russellrao', 'seuclidean', 'sokalmichener', 'sokalsneath',
          'sqeuclidean', 'yule']

        See the documentation for scipy.spatial.distance for details on these
        metrics.

        - any collable function (e.g., distance functions in proxi.utils.distance module)


    p : int, optional, default = 2
        Parameter for the Minkowski metric from
        sklearn.metrics.pairwise.pairwise_distances. When p = 1, this is
        equivalent to using manhattan_distance (l1), and euclidean_distance
        (l2) for p = 2. For arbitrary p, minkowski_distance (l_p) is used.

    metric_params : dict, optional, default = None
        Additional keyword arguments for the scipy metric function.

    OTU_column : string, optional, default = None
        Name of the DataFrame column that contains the OTUs IDs (i.e., nodes IDs).
        If OTU_column is None, the first column in the dataframe is treated as the OTU_column.

    is_undirected : bool, optional, default = True
        whether to compute undirected/directed graph. Default is undirected.

    is_weighted : bool, optional, default = False
        whether to compute weighted graph. Default is unweighted.

    is_normalize_samples : bool, optional, default = True
        whether to normalize each sample (i.e., column in the input data).

    is_standardize_otus : bool, optional, default = True
        whether to standardize each OTU (i.e., row in the input data)


    Returns
    -------
        nodes_id : array_like
            list of nodes.
        _A : scipy sparse matrix
            Adjacency matrix of the constructed graph.


    Examples
    --------
    >>> df = pd.read_csv(in_file)

    >>> # construct kNN-graph
    >>> nodes, a = get_knn_graph(df, 5,  metric='braycurtis')


    >>> # Note that a is a sparse matrix.
    >>> # Use 'todense' to convert a into numpy matrix format required for NetworkX
    >>> a = a.todense()
    >>> print('Shape of adjacency matris is {}'.format(np.shape(a)))

    >>> # save the constructed graph in graphml format
    >>> save_graph(a, nodes, out_file)

    """

    # get nodes id
    if OTU_column is None:
        node_id_column = data.columns[0]
    else:
        node_id_column = OTU_column
    nodes_id = data[node_id_column].values

    # get data as numpy array
    X = data.drop([node_id_column], axis=1).values
    num_nodes, num_samples = np.shape(X)

    # normalize samples (i.e., columns)
    if is_normalize_samples:
        X = normalize(X, norm='l1', axis=0)

    # standardize OTUs (i.e., rows)
    if is_standardize_otus:
        X = StandardScaler().fit_transform(X.T, None).T  # standardize OTUs (rows) -- Yes. Used with RMT method

    # Construct kNN-graph
    # _A is sparse matrix in CSR format
    _A = kneighbors_graph(X, n_neighbors=k, mode='connectivity', metric=metric, p=p, metric_params=metric_params)

    # check if you need to convert the directed graph into undirected
    if is_undirected:
        _rows, _cols = _A.nonzero()
        _len = len(_rows)
        for i in range(_len):
            _A[_cols[i], _rows[i]] = 1.0  # use _A[_rows[i], _cols[i]] if _A is weighted

    return nodes_id, _A
