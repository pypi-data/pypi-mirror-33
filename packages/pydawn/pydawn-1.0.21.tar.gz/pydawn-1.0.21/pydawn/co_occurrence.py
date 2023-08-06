# coding=utf-8

import pandas as pd
import numpy as np
import networkx as nx
import sys
import matplotlib.pyplot as plt
from igraph import *

reload(sys)
sys.setdefaultencoding('utf-8')


def gen_co_occurrence_matrix(keyword_with_year_csv, top_keyword_num=60):
    keyword_count = {}
    for line in open(keyword_with_year_csv):
        parts = line.split("|")
        if len(parts) < 2:
            continue

        for keyword in parts[:-1]:
            keyword = keyword.strip()
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

    # sort keyword
    top_keywords = []
    keyword_count_sorted = sorted(keyword_count.items(), key=lambda a: a[1], reverse=True)
    for index, item in enumerate(keyword_count_sorted):
        if index == top_keyword_num:
            break
        top_keywords.append(item[0])

    co_occurrence_matrix = pd.DataFrame(np.zeros(shape=(top_keyword_num, top_keyword_num)), columns=top_keywords, index=top_keywords)
    for line in open(keyword_with_year_csv):
        parts = line.split("|")
        if len(parts) < 2:
            continue

        for keyword1 in parts[:-1]:
            if keyword1 not in top_keywords:
                continue
            for keyword2 in parts[:-1]:
                if keyword2 not in top_keywords:
                    continue
                if keyword1 == keyword2:
                    continue
                co_occurrence_matrix.loc[keyword1, keyword2] += 1

    return co_occurrence_matrix


def calculate_yaccord_matrix(co_occurrence_matrix):
    row_num, col_num = co_occurrence_matrix.shape
    yaccord_matrix = pd.DataFrame(np.zeros(shape=(row_num, col_num)), index=co_occurrence_matrix.index, columns=co_occurrence_matrix.columns)
    occurrence_sum = co_occurrence_matrix.sum()

    for row in range(0, row_num):
        for col in range(0, col_num):
            co_occurrence = co_occurrence_matrix.iloc[row, col]
            if co_occurrence == 0:
                continue

            yaccord = 1.0 * co_occurrence / (occurrence_sum.iloc[row] + occurrence_sum.iloc[col] + 0.000001)
            yaccord_matrix.iloc[row, col] = yaccord

    return yaccord_matrix


def detect_cluster(G):
    clusters = []
    for cluster_peers in nx.find_cliques(G):
        print cluster_peers
    return clusters


if __name__ == '__main__':
    # keyword_count_file = "keyword_count.csv"
    # keywords_file = "keywords.txt"
    # calculate_yaccord_matrix(keyword_count_file, keywords_file, "test")
    co_occurrence_matrix = gen_co_occurrence_matrix("keywords_with_year.txt")
    # co_occurrence_matrix.to_csv("keywords_co_occurrence_matrix.txt")
    yaccord_matrix = calculate_yaccord_matrix(co_occurrence_matrix)
    #yaccord_matrix.to_csv("keywords_yaccord_matrix.csv")
    g = Graph.Adjacency(yaccord_matrix.values.tolist())
    print g.community_leading_eigenvector()
    # print co_occurrence_matrix.values
    #G = nx.from_numpy_matrix(co_occurrence_matrix.values)
    #nx.draw_networkx(G)
    #plt.show()
    # print detect_cluster(G)
