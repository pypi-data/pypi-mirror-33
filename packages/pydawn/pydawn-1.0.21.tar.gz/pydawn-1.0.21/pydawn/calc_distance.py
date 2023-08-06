# coding=utf-8


def calc_distance(dhash1, dhash2):
    difference = (int(dhash1, 16)) ^ (int(dhash2, 16))
    return bin(difference).count("1")


if __name__ == '__main__':

    dhash_dict = {}
    for line in open("dhash.result.2018_06_07_14"):
        line = line.strip()
        dhash_dict[line.split(",")[0]] = line.split(",")[1]

    result_dict = {}
    for key0, value0 in dhash_dict.items():
        for key1, value1 in dhash_dict.items():
            if key0 == key1:
                continue
            distance = calc_distance(value0, value1)
            result_dict["%s,%s" % (key0, key1)] = distance

    sorted_burst_dict = sorted(result_dict.iteritems(), key=lambda d: d[1], reverse=False)

    result = open("java_distance.csv", "w+")

    for item in sorted_burst_dict:
        result.write("%s,%s\n" % (item[0], item[1]))

    result.close()
