#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from named_redirect.skeleton import fib

__author__ = "Anish Mangal"
__copyright__ = "Anish Mangal"
__license__ = "gpl3"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
