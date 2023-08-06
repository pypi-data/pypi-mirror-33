#!/usr/bin/env python
# Copyright (c) 2018 Francesco Bartoli
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# -*- coding: utf-8 -*-

"""Tests for `marmee` package."""

import pytest
from marmee.marmee import Marmee

@pytest.fixture
def set_inputs():
    inputs = {}
    return inputs


class TestMarmee(object):
    """docstring for testing marmee."""

    cls = Marmee

    def test_is_marmee(self):
        try:
            self.cls().is_marmee()
        except (NotImplementedError, TypeError):
            assert True
