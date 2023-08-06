#!/usr/bin/env python
import sys

# os
platform = sys.platform.lower()
freebsd = "freebsd" in platform
linux = "linux" in platform
mac = "darwin" in platform
osx = "darwin" in platform
windows = "win32" in platform or "cygwin" in platform
cygwin = "cygwin" in platform
unix = not windows and not cygwin

# python versions
py2 = sys.version_info[0] == 2
py3 = sys.version_info[0] == 3
CI = sys.version_info[0] == 3
