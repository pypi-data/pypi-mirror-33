# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et tw=72 cc=+8
import doctest
from visaplan.kitchen import spoons

def load_tests(loader, tests, ignore):
    # https://docs.python.org/2/library/unittest.html#load-tests-protocol
    for mod in (
            spoons,
            ):
        tests.addTests(doctest.DocTestSuite(mod))
    return tests
