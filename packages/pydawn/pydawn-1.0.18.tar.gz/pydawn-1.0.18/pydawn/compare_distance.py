# coding=utf-8
import math

if __name__ == '__main__':
    java_distance = {}
    python_distance = {}

    for line in open("java_distance.csv"):
        parts = line.strip().split(",")
        python_distance[",".join(sorted([parts[0], parts[1]]))] = parts[2]

    for line in open("python_distance_lan.csv"):
        parts = line.strip().split(",")
        java_distance[",".join(sorted([parts[0], parts[1]]))] = parts[2]

    count_dict = {}
    for key, python_dist in python_distance.items():
        java_dist = java_distance[key]

        diff = int(math.fabs(int(python_dist) - int(java_dist)))
        if str(diff) in count_dict:
            count_dict[str(diff)] += 1
        else:
            count_dict[str(diff)] = 0

    count_dict_sorted = sorted(count_dict.iteritems(), key=lambda d: int(d[0]), reverse=False)
    total = sum(count_dict.values())
    for item in count_dict_sorted:
        print "%s,%s,%.3f%%" % (item[0], item[1], 1.0 * int(item[1])/total*100)


