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
Miscellaneous Python methods for proxi project.
"""

import numpy as np
import networkx as nx


__all__= ['aggregate_graphs',
          'filter_edges_by_votes',
          'save_graph',
          'summarize_graph',
          'jaccard_graph_similarity',
          'get_graph_object',
          'get_collable_name'
]


def aggregate_graphs (G, min_num_edges, is_weighted=False):
    """
    Aggregate the adjaceny matrices of graphs defined over the same set of nodes.

    Parameters
    ----------
    G : list of array_like matrices of shape (N,N)
        list of adjacency matrices.

    min_num_edges : int
        min number of edges between two nodes required to keep an edge between them in the aggregated graph.

    is_weighted : bool, optional, default = False
        whether to conmpute a weighted aggregated graph.

    Returns
    -------
        rVal : agregated graph
        W : edge weights (None if is_weighted is False)

    """

    num_graphs = len(G)

    rVal = np.copy(G[0])
    for i in range(1,num_graphs):
        rVal += G[i]

    no_edge_indeces = np.where(rVal<min_num_edges)

    W = None
    if is_weighted:
        W = rVal/float(num_graphs)
        W[no_edge_indeces] = 0


    rVal[no_edge_indeces] = 0
    rVal[np.where(rVal>0)] = 1

    return rVal, W


def filter_edges_by_votes (A, G, min_num_votes):
    """
    Aggregate the adjaceny matrices of a list of graphs G and use the aggregated graph to decide which edges
    in the base graph A to keep. All graphs are assumed to be defined over the same set of nodes.


    Parameters
    ----------
    A : array_like, shape(N,N)
        adjaceny matrix of the base graph.

    G : list of array_like matrices of shape (N,N)
        list of adjacency matrices.

    min_num_votes : int
        minimum number of edges between two nodes in the aggregated graph required to keep their edge (if exist)
        in the base graph.



    Returns
    -------
        rVal : array_like, shape(N,N)
            adjaceny matrix of the filtered base graph.
        W : array_like, shape(N,N)
            edge wesights associated with rVal graph

    """

    _adj, votes = aggregate_graphs(G, min_num_votes, is_weighted=True)
    _mnv = min_num_votes/float(len(G))

    W = np.multiply(A,votes)
    rVal = np.zeros_like(A)
    edge_indeces = np.where(W>=_mnv)
    rVal[edge_indeces] = 1.

    return rVal, W

# New version for saving a weighted graph in graphml format
# Date: March 22, 2018
# Tested: Yes


def save_graph(A, nodes_id, out_file, create_using=None):
    """
    Save the graph in graphml format.

    Parameters
    ----------
    A : array_like, shape(N,N)
        adjaceny matrix of the base graph.

    nodes_id : array-like, shape(N,)
        list of modes id

    out_file : file or string
        File or filename to write. Filenames ending in .gz or .bz2 will be compressed.

    create_using : Networkx Graph object, optional, default is Graph
        User specified Networkx Graph type.
        Accepted types are: Undirected Simple	Graph
                Directed Simple	DiGraph
                With Self-loops	Graph, DiGraph
                With Parallel edges	MultiGraph, MultiDiGraph

    Notes
    -----
    This implementation, based on networkx write_graphml method, does not support mixed graphs (directed
    and unidirected edges together) hyperedges, nested graphs, or ports.

    """

    graph_obj = nx.from_numpy_array(A, create_using=create_using)
    _mapping = {}
    num_nodes = len(nodes_id)
    count = 0
    for i in range(num_nodes):
        _mapping[count] = nodes_id[i]
        count += 1

    graph_obj = nx.relabel_nodes(graph_obj, _mapping, copy=False)
    of = open(out_file, 'wb')
    nx.write_graphml(graph_obj, of)


# New version for saving a weighted graph in graphml format
# Date: March 21, 2018
# Tested: Yes

def save_weighted_graph(A, nodes_name, weights, out_file, create_using=None):
    graph_obj = nx.from_numpy_array(A, create_using=create_using)
    weight_dict = {}
    for edge in graph_obj.edges():
        i, j = edge
        #weight_dict[edge] = {'weight': weights[i,j]}
        weight_dict[edge] = float(weights[i, j])


    nx.set_edge_attributes(graph_obj, weight_dict, 'weight')


    _mapping = {}
    num_nodes = len(nodes_name)
    count = 0
    for i in range(num_nodes):
        _mapping[count] = nodes_name[i]
        count += 1
    graph_obj = nx.relabel_nodes(graph_obj, _mapping, copy=False)

    of = open(out_file, 'wb')
    nx.write_graphml(graph_obj, of)



def summarize_graph(G):
    """
    Report basic summary statistics of a networkx graph object.

    Parameters
    ----------
    G : graph
        A networkx graph object

    Returns
    -------
        A dictionary of basic graph properties.

    """
    summary = {}
    summary ['# components'] = nx.number_connected_components(G)
    summary ['clustering coeffecient'] = nx.average_clustering(G)
    summary ['diameter']= nx.diameter(G)
    bc =  nx.betweenness_centrality(G).values()
    summary['betweenness centrality'] = sum(bc)/len(bc)
    return summary


def jaccard_graph_similarity(G1,G2):
    """
    Compute Jaccard similarity between two graphs over the same set of nodes.

    Parameters
    ----------
    G1 : graph
        A networkx graph object.

    G2 : graph
        A networkx graph pbject.

    Returns
    -------s
    Compute Jaccard similarity between two graphs over the same set of nodes.
    """

    num_common_edges = nx.number_of_edges(nx.intersection(G1,G2))
    num_edges_G1 = nx.number_of_edges(G1)
    num_edges_G2 = nx.number_of_edges(G2)
    return float(num_common_edges)/(num_edges_G1+num_edges_G2-num_common_edges)

def get_graph_object(A, nodes_id=None):
    """
    Construct a networkx graph object given an adjaceny matrix and nodes IDs.

    Parameters
    ----------
    A : array_like, shape(N,N)
        adjaceny matrix of the base graph.


    nodes_id : array-like, shape(N,)
        list of modes id


    Returns
    -------
    A networkx graph object.

    """
    graph_obj = nx.from_numpy_array(A)
    if nodes_id is not None:
        _mapping = {}
        num_nodes = len(nodes_id)
        count = 0
        for i in range(num_nodes):
            _mapping[count] = nodes_id[i]
            count += 1
        graph_obj = nx.relabel_nodes(graph_obj, _mapping, copy=False)
    return graph_obj


def get_collable_name(func):
    """
    Return the name of a collable function.

    Parameters
    ----------
    func : collable function

    Returns
    -------
    The name of a collable function.

    Notes
    -----
    str(func) returns <function neg_correlation at 0x1085cdd08>.


    """
    return func.split()[1]


