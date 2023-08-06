# coding=utf-8
import pbs
import re

if __name__ == '__main__':
    pattern = re.compile("\[.*?\]([^.]*)")
    str_test = "[Svara, James H.] Arizona State Univ, Sch Publ Affairs, Tempe, AZ 85287 USA. [Svara, James H.] Arizona State Univ, Ctr Urban Innovat, Tempe, AZ 85287 USA."
    match = pattern.findall(str_test)

    for line in match:
        print line
