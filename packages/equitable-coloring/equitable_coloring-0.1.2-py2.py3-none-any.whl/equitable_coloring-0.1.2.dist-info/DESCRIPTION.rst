========
Overview
========



Equitable coloring for networkX_ graphs.

.. _networkX: https://networkx.github.io/

From Wikipedia_:

    In graph theory [..] an equitable coloring is an assignment of colors to the vertices of an undirected graph, in such a way that

    + No two adjacent vertices have the same color, and
    + The numbers of vertices in any two color classes differ by at most one.


`Kierstead et. al. <https://link.springer.com/article/10.1007%2Fs00493-010-2483-5>`_ have provided a fast polynomial time algorithm for uncovering an equitable coloring using ``r + 1`` colors for a graph with maximum degree ``r``.
This package is an implementation of the algorithm for networkX graphs.

.. _Wikipedia: https://en.wikipedia.org/wiki/Equitable_coloring

* Free software: MIT license

Installation
============

::

    pip install equitable-coloring


Usage
=====

To use ``equitable-coloring``::

        >>> import networkx as nx
        >>> from equitable_coloring import equitable_color
        >>> from equitable_coloring.utils import is_equitable
        >>> G = nx.cycle_graph(4)
        >>> d = equitable_color(G, num_colors=3)
        >>> is_equitable(G, d)
        True


Documentation
=============

https://equitable-coloring.readthedocs.io/

Development
===========

To run the all tests run::

    pip install pytest-cov  # Needed the first time.
    python setup.py test


Or, you can use ``tox``.


Changelog
=========

0.1.2 (2018-06-30)
------------------

* Update README and usage instructions.


0.1.1 (2018-06-30)
------------------

* Initial version with tests.

0.1.0 (2018-06-11)
------------------

* First commit.


