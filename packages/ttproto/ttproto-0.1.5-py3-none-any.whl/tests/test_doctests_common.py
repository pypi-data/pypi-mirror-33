import doctest
import unittest
import ttproto.tat_coap.common

# python3 -m unittest tests/test_doctests_common.py -vvv

suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(ttproto.tat_coap.common))
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
