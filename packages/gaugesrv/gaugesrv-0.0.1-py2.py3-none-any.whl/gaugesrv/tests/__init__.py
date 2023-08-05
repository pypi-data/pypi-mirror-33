import unittest
from os.path import dirname


def make_suite():  # pragma: no cover
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        'gaugesrv.tests', pattern='test_*.py',
    )
    return test_suite
