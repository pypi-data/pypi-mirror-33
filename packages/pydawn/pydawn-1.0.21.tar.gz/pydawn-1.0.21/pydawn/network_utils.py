# coding=utf-8

from igraph import *
import numpy as np


def numpy_array_to_igraph(a):
    edge_list = []
    for row in a:
        edge_list.extend(v2 for v2, element in row if element > 0)
    return Graph(edge_list, directed=True)

if __name__ == '__main__':
    a = np.random.randn(6, 6)
    g = Graph.Adjacency(a.tolist())
    print g.community_leading_eigenvector()

