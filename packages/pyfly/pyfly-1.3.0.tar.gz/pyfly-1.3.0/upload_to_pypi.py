import os

here_is = os.path.dirname(__file__)
_setup = os.path.join(here_is, "setup.py")
# _pyfly = os.path.join(here_is, "pyfly")
# os.system("python3 -m compileall -b %s" % _pyfly)
os.system("python3 %s sdist upload" % _setup)