..  -*- coding: utf-8 -*-

.. _contents:

Overview
========

Proxi is a Python package for proximity graph construction. In proximity graphs, each node is connected by an
edge (directed or undirected) to its nearest neighbors according to some distance metric *d*.

Proxi provides tools for inferring different types of proximity graphs from an OTU table including:

-  k Nearest Neighbor kNN-graphs
-  radius Nearest Neighbor rNN-graphs
-  Perturbed k Nearest Neighbor pkNN-graphs

In addition, Proxi provides functionality for inferring pairwise graphs using virtually any user-defined proximity metric as well as support for aggregating graphs.


Audience
--------

The audience for Proxi includes bioinformaticians, mathematicians, physicists, biologists,
computer scientists, and social scientists. Although Proxi was developed with metagenomics data in mind, 
the tool is applicable to other types of data including (but not limited to) gene expression, protein-protein interaction,
wireless networks, images, etc.

Citing
------


Documentation
-------------

.. only:: html

    :Release: |version|
    :Date: |today|


.. toctree::
   :maxdepth: 4

   INSTALL
   README
   proxi
   Tutorials

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




