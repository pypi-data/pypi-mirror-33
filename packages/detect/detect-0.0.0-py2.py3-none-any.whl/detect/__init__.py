#!/usr/bin/env python
import sys

print(sys.version_info)

# os
freebsd = "freebsd".lower() in sys.platform.lower()
linux = "linux".lower() in sys.platform.lower()
mac = "darwin".lower() in sys.platform.lower()
windows = "win32".lower() in sys.platform.lower()
cygwin = "cygwin".lower() in sys.platform.lower()
unix = not windows and not cygwin

# python versions
py2 = sys.version_info[0] == 2
py3 = sys.version_info[0] == 3
CI = sys.version_info[0] == 3
