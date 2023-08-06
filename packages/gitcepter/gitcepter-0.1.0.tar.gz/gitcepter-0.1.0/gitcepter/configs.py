# -*- coding: utf-8 -*-
import sys

from gitcepter.checks import Checkstyle, JsonCheck, XmlCheck, CommitMessageCheck

checks = []

message = open(sys.argv[1], "r").readline()
# commit message
checks.append(CommitMessageCheck(message))

# checkstyle
checks.append(Checkstyle("config/checkstyle/checkstyle.xml"))

# json style
checks.append(JsonCheck())

# xml style
checks.append(XmlCheck())
