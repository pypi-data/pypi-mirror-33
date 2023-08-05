# coding=utf-8
import hashlib
import re
from urlparse import urlparse

import chardet


def gen_md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def refine_urls(host, seed_url, urls):
    urls = sorted(list(set(urls)))
    refined_urls = []
    seed_uri = urlparse(seed_url)
    for url in urls:
        uri = urlparse(url)
        if len(uri.netloc) == 0:
            path = seed_uri.path + url
            path = path.replace("//", "/")
            url = seed_uri.scheme + "://" + seed_uri.netloc + path
        elif url.find(host) == -1:
            continue

        refined_urls.append(url.strip())

    refined_urls = sorted(list(set(refined_urls)))
    return refined_urls


def get_links(host, seed_url, html):
    url_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return refine_urls(host, seed_url, url_regex.findall(html))


def detect_str_charset(content):
    result = chardet.detect(content)
    encoding = result['encoding']
    if encoding is None:
        encoding = "utf-8"
    return encoding.lower()


def convert_string_to_utf8(content):
    char_set = detect_str_charset(content)
    content = content.decode(char_set, errors="ignore").encode("utf-8")
    return content


def pick_charset(html):
    charset = None
    m = re.compile('<meta .*(http-equiv="?Content-Type"?.*)?charset="?([a-zA-Z0-9_-]+)"?', re.I).search(html)
    if m and m.lastindex == 2:
        charset = m.group(2).lower()
    return charset


if __name__ == '__main__':
    content = open("test.html").read()
    content = pick_charset(content)
    print content

