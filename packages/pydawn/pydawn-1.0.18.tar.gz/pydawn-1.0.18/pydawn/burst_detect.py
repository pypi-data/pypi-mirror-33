# coding=utf-8

import burst_detection as bd
import re
import matplotlib.pyplot as pl
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator, FuncFormatter
import sys

from pydawn.co_occurrence import calculate_yaccord_matrix

reload(sys)
sys.setdefaultencoding('utf-8')


def burst_detect(r, d, label, gamma=1):
    # number of time points
    n = len(r)

    # find the optimal state sequence (q)
    q, d, r, p = bd.burst_detection(r, d, n, s=3, gamma=gamma, smooth_win=1)

    # enumerate bursts based on the optimal state sequence
    bursts = bd.enumerate_bursts(q, label)

    # find weight of bursts
    weighted_bursts = bd.burst_weights(bursts, r, d, p)

    if len(weighted_bursts) > 0:
        print weighted_bursts


def detect_burst_words(start_year, end_year, keywords_with_year_file, keyword_count_file, top_keywords_num=60, tag="", gamma=1, delimiter="|"):
    ori_stdout = sys.stdout
    burst_raw_file = "burst_result_raw_%s.txt" % tag
    f = open(burst_raw_file, 'w+')
    sys.stdout = f

    year_range = end_year - start_year + 1

    top_keywords = []
    top_keywords_dict = {}
    top_keywords_count_dict = {}

    count = 0
    for line in open(keyword_count_file):
        keyword = line.split(delimiter)[0]
        top_keywords_count_dict[keyword] = int(line.split(delimiter)[1])
        top_keywords.append(keyword)
        top_keywords_dict[keyword] = count

        count += 1
        if count >= top_keywords_num:
            break

    keywords_freq_by_year = np.zeros(shape=(top_keywords_num, year_range))
    for line in open(keywords_with_year_file):
        keywords = line.split(delimiter)
        year = int(keywords[-1]) - start_year
        for index, keyword in enumerate(keywords):
            if index != len(keywords)-1 and keyword in top_keywords:
                keywords_freq_by_year[top_keywords_dict[keyword]][year] += 1

    all_keyword_sum = np.sum(keywords_freq_by_year, axis=0)

    for index, year_count in enumerate(keywords_freq_by_year):
        keyword = top_keywords[index]
        try:
            burst_detect(year_count, all_keyword_sum, keyword, gamma)
        except:
            #print "%s burst exception" % keyword
            pass

    f.close()
    sys.stdout = ori_stdout

    burst_file = open("burst_detection_%s.csv" % tag, "w+")

    burst_dict = {}
    for line in open(burst_raw_file):
        line = line.strip()
        if len(line) == 0 or line.find("label") != -1:
            continue

        parts = re.split("\s*", line)
        begin = int(parts[2]) + start_year
        end = int(parts[3]) + start_year
        line = "%s,%s,%s,%s\n" % (parts[1], parts[2], parts[3], parts[4])
        burst_dict[line] = begin

    sorted_burst_dict = sorted(burst_dict.iteritems(), key=lambda d: d[0], reverse=False)
    for item in sorted_burst_dict:
        print item[0]
        burst_file.write(item[0])

    burst_file.close()


def draw_burst(start_year, end_year, tag=""):
    burst_file = "burst_detection_%s.csv" % tag

    pl.figure(figsize=(10, 6))
    ax = pl.gca()
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    pl.subplots_adjust(bottom=0.15)
    pl.grid()

    keyword_list = []
    for index, line in enumerate(open(burst_file)):
        parts = line.split(",")
        if parts[0].strip() not in keyword_list:
            keyword_list.append(parts[0].strip().decode("utf-8"))

    pl.axis([start_year, end_year + 1, -1, len(keyword_list)])

    def keyword_format(index, pos):
        index = int(index)

        if index < 0 or index > len(keyword_list)-1:
            return ""
        return keyword_list[index]

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_formatter(FuncFormatter(keyword_format))
    ax.yaxis.set_major_locator(MultipleLocator(1))

    for line in open(burst_file):
        parts = line.split(",")

        weight = parts[3].strip()

        start = int(parts[1]) + start_year
        end = int(parts[2]) + start_year

        x = np.arange(start, end + 1, 1)
        y = np.empty(end - start + 1)
        index = keyword_list.index(parts[0].strip())
        y[:] = index
        pl.plot(x, y, linewidth=4, color="green")

        if weight != '0':
            pl.text(x[0], y[0], weight)

        if start == end:
            pl.scatter(start, index, color="green")

    pl.show()


if __name__ == '__main__':
    tag = "ssci"
    start = 2000
    end = 2017
    keyword_count_file = "keywords_count_%s.csv" % tag
    keywords_file = "keywords_%s.txt" % tag
    keywords_with_year_file = "keywords_with_year_%s.csv" % tag
    detect_burst_words(start, end, keywords_with_year_file, keyword_count_file, tag=tag, gamma=1)
    draw_burst(start, end, tag)
    calculate_yaccord_matrix(keyword_count_file, keywords_with_year_file, tag)

