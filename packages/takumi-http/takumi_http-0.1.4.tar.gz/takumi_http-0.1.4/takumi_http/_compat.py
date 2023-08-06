# -*- coding: utf-8 -*-


import sys

PY2 = sys.version_info[0] == 2

if PY2:
    integer_types = (int, long)
    string_types = (str, unicode)

else:
    integer_types = (int, )
    string_types = (str,)
