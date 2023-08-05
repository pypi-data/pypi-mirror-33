from __future__ import unicode_literals

import pytest

from vr.server import models as M


@pytest.mark.parametrize(
    ['data', 'expected'],
    [
        (1, 'c4ca4238a0b923820dcc509a6f75849b'),
        ('a', '6067924ae1b1832abce3d12fe83755a9'),
        ({}, '99914b932bd37a50b983c5e7c90ae93b'),
        (set(), 'd751713988987e9331980363e24189ce'),
        ([], 'd751713988987e9331980363e24189ce'),
        ((), 'd751713988987e9331980363e24189ce'),
        (b'\xa3', 'dd335aa90459c69348d739b1628dcf86'),
        ('\xa3', 'dd335aa90459c69348d739b1628dcf86'),
    ],
)
def test_make_hash(data, expected):
    assert M.make_hash(data) == expected
