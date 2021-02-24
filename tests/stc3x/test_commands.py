# -*- coding: utf-8 -*-
# (c) Copyright 2020 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import pytest
from sensirion_i2c_driver.errors import I2cNackError

# from sensirion_i2c_stc.stc3x.response_types import
from sensirion_i2c_stc.stc3x.data_types import Stc31BinaryGas
from sensirion_i2c_stc.stc3x.response_types import Stc3xGasConcentration, \
    Stc3xTemperature


@pytest.mark.needs_device
@pytest.mark.needs_stc3x
@pytest.mark.parametrize("binary_gas", [
    Stc31BinaryGas.Co2InAirRange25,
    Stc31BinaryGas.Co2InAirRange100,
])
def test_set_binary_gas_and_measure(stc3x, binary_gas):
    """
    Test set binary gas and measure
    """
    stc3x.set_bianry_gas(binary_gas)
    gas_concentration, temperature = stc3x.measure_gas_concentration()

    assert type(gas_concentration) is Stc3xGasConcentration
    assert type(gas_concentration.ticks) is int
    assert type(gas_concentration.vol_percent) is float

    assert type(temperature) is Stc3xTemperature
    assert type(temperature.ticks) is int
    assert type(temperature.degrees_celsius) is float
    assert type(temperature.degrees_fahrenheit) is float


@pytest.mark.needs_device
@pytest.mark.needs_stc3x
@pytest.mark.parametrize("expected_temperature", [
    23.12,
    12.5
])
def test_set_temperature(stc3x, expected_temperature):
    """
    Test set temperature. The first temperature returned from the measure cmd
    is defined to be the same as previously set using set_temperature.
    """
    stc3x.set_bianry_gas(Stc31BinaryGas.Co2InAirRange100)
    stc3x.set_temperature(expected_temperature)
    _, temperature = stc3x.measure_gas_concentration()
    assert temperature.degrees_celsius == expected_temperature


@pytest.mark.needs_device
@pytest.mark.needs_stc3x
def test_enable_sleep_mode(stc3x):
    """
    Test sleep mode
    """
    stc3x.enable_sleep_mode()
    try:
        stc3x.set_bianry_gas(Stc31BinaryGas.Co2InAirRange100)
    except I2cNackError:
        assert True
    else:
        assert False, "STC3x is sleeping"

    # Now the sensor should be awake, according to the datasheet.

    try:
        stc3x.set_bianry_gas(Stc31BinaryGas.Co2InAirRange100)
        _, _ = stc3x.measure_gas_concentration()
    except I2cNackError:
        assert False, "STC3x should be awake after previous interaction"
    else:
        assert True


@pytest.mark.needs_device
@pytest.mark.needs_stc3x
def test_self_test(stc3x):
    expected_result = 0
    result = stc3x.perform_self_test()
    assert result == expected_result


@pytest.mark.needs_device
@pytest.mark.needs_stc3x
def test_read_product_identifier(stc3x):
    expected_stc31_product_number = 0x08010301
    product_number, serial_number = stc3x.read_product_identifier()
    assert product_number == expected_stc31_product_number
    assert type(serial_number) is int
    assert serial_number > 1e18
