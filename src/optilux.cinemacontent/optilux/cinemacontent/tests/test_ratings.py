import doctest

from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

def test_suite():
    return layered(
            doctest.DocTestSuite('optilux.cinemacontent.ratings'),
            layer=UNIT_TESTING
        )
