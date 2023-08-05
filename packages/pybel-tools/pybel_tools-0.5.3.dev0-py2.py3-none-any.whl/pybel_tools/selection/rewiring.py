# -*- coding: utf-8 -*-

"""

This module has functions that help produce random permutations over networks.

Random permutations are useful in statistical testing over aggregate statistics.

"""

import random

from pybel.constants import RELATION
from .. import pipeline


def is_edge_consistent(graph, u, v):
    """Checks if all edges between two nodes have the same relation

    :param pybel.BELGraph graph: A BEL Graph
    :param tuple u: The source BEL node
    :param tuple v: The target BEL node
    :return: If all edges from the source to target node have the same relation
    :rtype: bool
    """
    if not graph.has_edge(u, v):
        raise ValueError('{} does not contain an edge ({}, {})'.format(graph, u, v))

    return 0 == len(set(d[RELATION] for d in graph.edge[u][v].values()))


def all_edges_consistent(graph):
    """Returns if all edges are consistent in a graph. Wraps :func:`pybel_tools.utils.is_edge_consistent`

    :param pybel.BELGraph graph: A BEL graph
    :return: Are all edges consistent
    :rtype: bool
    """
    return all(is_edge_consistent(graph, u, v) for u, v in graph.edges_iter())


@pipeline.mutator
def rewire_targets(graph, p):
    """Rewires a graph's edges' target nodes


    - For BEL graphs, assumes edge consistency (all edges between two given nodes are have the same relation)
    - Doesn't make self-edges

    :param pybel.BELGraph graph: A BEL graph
    :param p: The probability of rewiring
    :return: A rewired BEL graph
    """

    if not all_edges_consistent(graph):
        raise ValueError('{} is not consistent'.format(graph))

    result = graph.copy()
    nodes = result.nodes()

    for u, v in result.edges():
        if random.random() < p:
            continue

        w = random.choice(nodes)

        while w == u or result.has_edge(u, w):
            w = random.choice(nodes)

        result.add_edge(w, v)
        result.remove_edge(u, v)

    return result
