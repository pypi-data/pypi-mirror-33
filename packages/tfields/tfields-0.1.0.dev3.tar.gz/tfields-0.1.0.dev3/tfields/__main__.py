"""
Run tests on module call with argument test
"""
import sys
import unittest
import doctest
import pathlib


def run_doctests():
    """
    Find all doctests and execute them
    """
    this_dir = pathlib.Path(__file__).resolve()
    for f in list(this_dir.glob('**/*.py')):
        doctest.testfile(str(f.relative_to(pathlib.Path.cwd().resolve())))  # , verbose=True, optionflags=doctest.ELLIPSIS)


def load_unittests(loader=None, suite=None):
    if loader is None:
        loader = unittest.TestLoader()
    if suite is None:
        suite = unittest.TestSuite()
    parent = pathlib.Path(__file__).parent.parent
    for f in list(parent.glob('*/test*.py')):
        sys.path.insert(0, str(f.parent))
        mod = __import__(f.name.rstrip('.py'))
        for test in loader.loadTestsFromModule(mod):
            suite.addTests(test)
        sys.path.remove(str(f.parent))
    return suite

def run_unittests():
    unittest.main(defaultTest='load_unittests')



if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg == 'test':
            print("Run doctests")
            run_doctests()
            print("Run unit tests")
            run_unittests()
