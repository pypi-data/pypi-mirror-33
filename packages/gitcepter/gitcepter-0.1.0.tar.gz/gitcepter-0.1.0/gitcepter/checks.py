# -*- coding: utf-8 -*-
import re
from subprocess import check_output

from gitcepter.file import file_exists, file_to_text
from gitcepter.log import info, error, warn
from gitcepter.precommit import get_changed_java_files, get_changed_json_files, get_changed_xml_files
from gitcepter.utils import java_exe_path


class BaseCheck(object):

    def check(self):
        pass


class Checkstyle(BaseCheck):

    def __init__(self, config_file):
        self.config_file = config_file

    def check(self):
        config_file = self.config_file
        if not self.config_file and not file_exists(config_file):
            """ 如果没有找到checkstyle配置文件,提示检查失败 """
            warn("config file not exists: '" + config_file + "'")
            return False

        changed_java_files = get_changed_java_files()

        info("执行checkstyle检查...")
        if len(changed_java_files) < 1:
            # print("没有java文件改动,已跳过checkstyle检查.")
            """ 如果没有java文件改动，直接跳过checkstyle检查 """
            return True

        args = [
            java_exe_path,
            '-jar',
            'libs/checkstyle.jar',
            '-c',
            config_file
        ]
        args.extend(changed_java_files)

        output = check_output(args).decode('utf-8')

        lines = output.splitlines()
        del lines[0]
        del lines[-1]

        if len(lines) > 0:
            for line in lines:
                print(line)
            error("checkstyle检查不通过,请检查后再执行commit")
            return False
        return True


class JsonCheck(BaseCheck):

    def check(self):
        info("执行json格式检查...")
        json_files = get_changed_json_files()
        from json import loads
        try:
            for file in json_files:
                loads(file_to_text(file))
        except Exception as e:
            error("json格式检查不通过:" + str(e))
            return False

        return True


class XmlCheck(BaseCheck):

    def check(self):
        info("执行xml格式检查...")
        xml_files = get_changed_xml_files()
        from xml.etree import ElementTree
        try:
            for file in xml_files:
                ElementTree.fromstring(file_to_text(file))
        except Exception as e:
            error("xml格式检查不通过:" + str(e))
            return False
        return True


class CommitMessageCheck(BaseCheck):
    regex = "\[((bugfix\]\s{0,2}\[[a-zA-Z0-9_\-]{1,24})|crash|(feature\]\s{0,2}\[[a-zA-Z0-9_\-]{1," \
            "24})|docs|style|refactor|test|chore)\].+"

    def __init__(self, commit_msg):
        self.commit_msg = commit_msg.strip()

    def check(self):
        info("执行commit规范检查...")
        if not re.match(self.regex, self.commit_msg):
            error("不符合commit规范: " + self.commit_msg)
            return False
        return True
