# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from enum import IntEnum


class Stc31BinaryGas(IntEnum):
    """
    An enum containing all available binary gas configuratinos for the STC31
    Sensor.
    """
    Co2InNo2Range100 = 0x0000  #: CO2 in N2 Range: 0 to 100 vol%
    Co2InAirRange100 = 0x0001  #: CO2 in air Range: 0 to 100 vol%
    Co2InNo2Range25 = 0x0002  #: CO2 in N2 Range: 0 to 25 vol%
    Co2InAirRange25 = 0x0003  #: CO2 in air Range: 0 to 25 vol%


class Stc3xRelativeHumidityConditionPercent(object):
    """
    Represents a relative humidity condition in percent.

    With the :py:attr:`ticks` you can access the raw data as sent to the
    device.

    :param float relative_humidity_percent:
        The relative humidity in percent.
    """

    def __init__(self, relative_humidity_percent):
        """
        Creates an instance from the configured condition.
        """

        #: The configured condition in percent.
        self.percent_rh = float(relative_humidity_percent)

        #: The ticks (int) to pass to the device.
        self.ticks = int(round(self.percent_rh * 65535 / 100.))

    def __str__(self):
        return '{:0.2f} %RH'.format(self.percent_rh)


class Stc3xTemperatureConditionDegC(object):
    """
    Represents a temperature condition in degree celsius.

    With the :py:attr:`ticks` you can access the raw data as sent to the
    device.

    :param float degree_celsius:
        The temperature as degree celsius
    """

    def __init__(self, degree_celsius):
        """
        Creates an instance from the configured condition.
        """

        #: The temperature condition in °C.
        self.degrees_celsius = float(degree_celsius)

        #: The temperature condition in °F.
        self.degrees_fahrenheit = 32. + (self.degrees_celsius * 9. / 5.)

        #: The ticks (int) to pass to the device.
        self.ticks = int(round(self.degrees_celsius * 200.))

    def __str__(self):
        return '{:0.1f} °C'.format(self.degrees_celsius)


class Stc3xReferenceConcentration(object):
    """
    Represents a reference gas concentration.

    With the :py:attr:`ticks` you can access the raw data delivered to the
    device.

    :param float vol_percent:
        The gas concentration in vol%.
    """

    def __init__(self, vol_percent):
        """
        Creates an instance from the provided raw data.
        """

        #: The concentration in vol%.
        self.vol_percent = float(vol_percent)

        #: The ticks (int) as received from the device.
        self.ticks = int(round((vol_percent * 32768.) / 100. + 16384.))

    def __str__(self):
        return '{:0.2f} vol%'.format(self.vol_percent)
