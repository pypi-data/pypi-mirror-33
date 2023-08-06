# coding=utf-8


def gen_statistics_data(extract_function, sample_dir, tag=""):
    keyword_count_file = "keyword_count_%s.csv" % tag
    keywords_file = "keywords_%s.txt" % tag
    keywords_with_year = "keywords_with_year_%s.txt" % tag
    paper_count_by_year = "paper_count_by_year_%s.csv" % tag
    author_location = "author_location_%s.txt" % tag

    pcby = open(paper_count_by_year, "w+")
    kf = open(keywords_file, "w+")
    kwy = open(keywords_with_year, "w+")
    kcf = open(keyword_count_file, "w+")
    al = open(author_location, "w+")
    keyword_dict = {}
    keyword_year_dict = {}

    for year, keywords, location in apply(extract_function, (sample_dir,)):
        for keyword in keywords:
            kf.write(keyword + "|")
            kwy.write(keyword + "|")

            if keyword not in keyword_dict:
                keyword_dict[keyword] = 1
            else:
                keyword_dict[keyword] += 1

            if year not in keyword_year_dict:
                keyword_year_dict[year] = 1
            else:
                keyword_year_dict[year] += 1

        kf.write("\n")
        kwy.write(year + "\n")
        if location is not None:
            al.write(location+"\n")

    kf.close()
    kwy.close()
    al.close()

    # sort key word
    sorted_keyword_dict = sorted(keyword_dict.iteritems(), key=lambda d: d[1], reverse=True)
    for item in sorted_keyword_dict:
        kcf.write("%s,%d\n" % (item[0], item[1]))

    kcf.close()

    sorted_keyword_year_dict = sorted(keyword_year_dict.iteritems(), key=lambda d: d[0], reverse=False)
    for item in sorted_keyword_year_dict:
        pcby.write("%s,%d\n" % (item[0], item[1]))
    pcby.close()



