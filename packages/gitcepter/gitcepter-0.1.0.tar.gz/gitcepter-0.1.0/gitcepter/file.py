# -*- coding: utf-8 -*-

import os.path


def file_extension(path):
    return os.path.splitext(path)[1]


def file_exists(path):
    return os.path.exists(path)


def file_to_text(path):
    f = open(path, "r", encoding='utf-8')
    return '\n'.join(f.readlines())
