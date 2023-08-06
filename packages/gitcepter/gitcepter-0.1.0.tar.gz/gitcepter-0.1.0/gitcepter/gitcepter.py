# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys
from subprocess import check_output
from sys import stdout
from traceback import print_exc

from gitcepter.utils import git_exe_path

from gitcepter.configs import checks
from gitcepter.log import error


def main():
    result = True

    try:
        for check in checks:
            result &= check.check()
    except Exception:
        # Flush the problems we have printed so far to avoid the traceback
        # appearing in between them.
        stdout.flush()
        error(file=sys.stderr)
        error('An error occurred, but the commits are accepted.', file=sys.stderr)
        print_exc()
    if result:
        """ 0表示成功 """
        return 0
    """ 非0表示失败 """
    error("代码提交失败，请修正后重新提交")
    print("")
    return 1



