import unittest
import os


def test_suite():
    test_loader = unittest.TestLoader()
    loc = getLoc()
    if loc is None:
        testSuite = test_loader.discover(loc + '/tests/standalone', pattern='doesnotexist*.py')
        # TODO: delete sym link?
    else:
        # Add sym link, which shouldn't be there yet since we don't want tests in our builds
        if not os.path.islink(loc + '/tests/standalone'):
            dirs = loc.split('/')
            backpath = '../'
            for x in range(0, len(dirs)):
                backpath += '../'
            os.symlink(backpath + "tests/standalone", loc + '/tests/standalone')
        testSuite = test_loader.discover(loc + '/tests/standalone', pattern='test*.py')
    return testSuite

def getLoc():
    """ return value of NAME from what is in the setup.py file"""
    with open('setup.py', 'r') as f:
        output = f.read()
        f.close()
    if output is None:
        return None
    lines = output.splitlines()
    keepReading = True
    length = len(lines)
    index = 0
    while keepReading and index < length:
        line = lines[index]
        if line.startswith("NAME =") or line.startswith("NAME="):
            name = line.split("=")[1]
            return name.strip().strip('"').strip("'").replace('.', '/')
        index += 1
