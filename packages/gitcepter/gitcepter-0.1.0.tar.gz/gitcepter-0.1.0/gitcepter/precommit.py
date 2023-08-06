# -*- coding: utf-8 -*-
from subprocess import check_output

from gitcepter.file import file_extension
from gitcepter.utils import git_exe_path

java_files = []
xml_files = []
json_files = []


def get_changed_java_files():
    if not java_files:
        category_files()
    return java_files


def get_changed_xml_files():
    if not xml_files:
        category_files()
    return xml_files


def get_changed_json_files():
    if not json_files:
        category_files()
    return json_files


def category_files():
    for file in get_changed_files().splitlines():
        extension = file_extension(file)
        if extension == ".java":
            java_files.append(file)
        if extension == ".json":
            json_files.append(file)
        if extension == ".xml":
            xml_files.append(file)


def get_changed_files():
    return check_output([
        git_exe_path,
        'diff',
        'HEAD',
        '--cached',
        '--name-only',
        '--diff-filter=ACMR'
    ]).decode('utf-8')
