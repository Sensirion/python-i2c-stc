# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_stc.stc3x.data_types import Stc3xTemperatureConditionDegC, \
    Stc3xRelativeHumidityConditionPercent, Stc3xReferenceConcentration
import pytest


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'degrees_celsius': 0, 'degrees_fahrenheit': 32.}),
    dict(
        {'ticks': 20000, 'degrees_celsius': 100., 'degrees_fahrenheit': 212.}),
    dict(
        {'ticks': -5000, 'degrees_celsius': -25., 'degrees_fahrenheit': -13.}),
])
def test_temperature_condition_degc(value):
    """
    Test if the Stc3xTemperatureConditionDegC() type works as expected for
    different values.
    """
    result = Stc3xTemperatureConditionDegC(value.get('degrees_celsius'))
    assert type(result) is Stc3xTemperatureConditionDegC
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.degrees_celsius) is float
    assert result.degrees_celsius == value.get('degrees_celsius')
    assert type(result.degrees_fahrenheit) is float
    assert result.degrees_fahrenheit == value.get('degrees_fahrenheit')


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'percent_rh': 0}),
    dict({'ticks': 65535, 'percent_rh': 100}),
    dict({'ticks': 36044, 'percent_rh': 55})
])
def test_relative_humidity_condition_percent(value):
    """
    Test if the Stc3xRelativeHumidityConditionPercent() type works as expected
    for different values.
    """
    result = Stc3xRelativeHumidityConditionPercent(value.get('percent_rh'))
    assert type(result) is Stc3xRelativeHumidityConditionPercent
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.percent_rh) is float
    assert result.percent_rh == value.get('percent_rh')


@pytest.mark.parametrize("value", [
    dict({'ticks': 16384, 'vol_percent': 0}),
    dict({'ticks': 0, 'vol_percent': -50}),
    dict({'ticks': 15892, 'vol_percent': -1.5})
])
def test_reference_concentration(value):
    """
    Test if the Stc3xReferenceConcentration() type works as expected for
    different values.
    """
    result = Stc3xReferenceConcentration(value.get('vol_percent'))
    assert type(result) is Stc3xReferenceConcentration
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.vol_percent) is float
    assert result.vol_percent == value.get('vol_percent')
