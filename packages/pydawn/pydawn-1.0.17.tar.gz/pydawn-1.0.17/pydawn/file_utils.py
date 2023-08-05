# coding=utf-8
import hashlib
import os
import chardet
import codecs


def get_file_md5(filename):
    if not os.path.isfile(filename):
        return
    file_hash = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        file_hash.update(b)
    f.close()
    return file_hash.hexdigest().upper()


def detect_file_charset(file_path):
    f = open(file_path, "rb")
    test_length = 1024
    data = f.read(test_length)
    result = chardet.detect(data)
    encoding = result['encoding']
    if encoding is None:
        encoding = "utf-8"
    return encoding.lower()


def open_file_in_utf8(file_path):
    encoding = detect_file_charset(file_path)
    f = codecs.open(file_path, encoding=encoding)
    return f


def list_file_recursively(sample_dir):
    g = os.walk(sample_dir)
    for path, d, file_list in g:
        for file_name in file_list:
            yield os.path.join(path, file_name)


if __name__ == '__main__':
    pass

