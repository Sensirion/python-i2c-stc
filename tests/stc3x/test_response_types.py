# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import pytest

from sensirion_i2c_stc.stc3x.response_types import Stc3xGasConcentration, \
    Stc3xTemperature


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'vol_percent': -50}),
    dict({'ticks': 16384, 'vol_percent': 0}),
    dict({'ticks': 15892, 'vol_percent': -1.5}),
])
def test_gas_concentration(value):
    """
    Test if the Stc3xGasConcentration() type works as expected for different
    values.
    """
    result = Stc3xGasConcentration(value.get('ticks'))
    assert type(result) is Stc3xGasConcentration
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.vol_percent) is float
    assert result.vol_percent == pytest.approx(value.get('vol_percent'), 0.01)


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'degrees_celsius': 0, 'degrees_fahrenheit': 32.}),
    dict(
        {'ticks': 20000, 'degrees_celsius': 100., 'degrees_fahrenheit': 212.}),
    dict(
        {'ticks': -5000, 'degrees_celsius': -25., 'degrees_fahrenheit': -13.}),
])
def test_temperature(value):
    """
    Test if the Stc3xTemperature() type works as expected for different values.
    """
    result = Stc3xTemperature(value.get('ticks'))
    assert type(result) is Stc3xTemperature
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.degrees_celsius) is float
    assert result.degrees_celsius == value.get('degrees_celsius')
    assert type(result.degrees_fahrenheit) is float
    assert result.degrees_fahrenheit == value.get('degrees_fahrenheit')
