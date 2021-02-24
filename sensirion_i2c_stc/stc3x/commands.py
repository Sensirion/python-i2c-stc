# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

# flake8: noqa

from __future__ import absolute_import, division, print_function

import logging
from struct import pack, unpack

from sensirion_i2c_driver import SensirionI2cCommand, CrcCalculator

from sensirion_i2c_stc.stc3x.data_types import \
    Stc3xRelativeHumidityConditionPercent, Stc3xTemperatureConditionDegC, \
    Stc3xReferenceConcentration
from sensirion_i2c_stc.stc3x.response_types import Stc3xTemperature, \
    Stc3xGasConcentration

log = logging.getLogger(__name__)


class Stc3xI2cCmdBase(SensirionI2cCommand):
    """
    STC3x I²C base command.
    """

    def __init__(self, command, tx_data, rx_length, read_delay, timeout,
                 post_processing_time=0.0):
        """
        Constructs a new STC3x I²C command.

        :param int/None command:
            The command ID to be sent to the device. None means that no
            command will be sent, i.e. only ``tx_data`` (if not None) will
            be sent. No CRC is added to these bytes since the command ID
            usually already contains a CRC.
        :param bytes-like/list/None tx_data:
            Bytes to be extended with CRCs and then sent to the I²C device.
            None means that no write header will be sent at all (if ``command``
            is None too). An empty list means to send the write header (even if
            ``command`` is None), but without data following it.
        :param int/None rx_length:
            Number of bytes to be read from the I²C device, including CRC
            bytes. None means that no read header is sent at all. Zero means
            to send the read header, but without reading any data.
        :param float read_delay:
            Delay (in Seconds) to be inserted between the end of the write
            operation and the beginning of the read operation. This is needed
            if the device needs some time to prepare the RX data, e.g. if it
            has to perform a measurement. Set to 0.0 to indicate that no delay
            is needed, i.e. the device does not need any processing time.
        :param float timeout:
            Timeout (in Seconds) to be used in case of clock stretching. If the
            device stretches the clock longer than this value, the transceive
            operation will be aborted with a timeout error. Set to 0.0 to
            indicate that the device will not stretch the clock for this
            command.
        :param float post_processing_time:
            Maximum time in seconds the device needs for post processing of
            this command until it is ready to receive the next command. For
            example after a device reset command, the device might need some
            time until it is ready again. Usually this is 0.0s, i.e. no post
            processing is needed.
        """
        super(Stc3xI2cCmdBase, self).__init__(
            command=command,
            tx_data=tx_data,
            rx_length=rx_length,
            read_delay=read_delay,
            timeout=timeout,
            crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
            command_bytes=2,
            post_processing_time=post_processing_time,
        )


class Stc3xI2cCmdSetBinaryGas(Stc3xI2cCmdBase):
    """
    Set Binary Gas I²C Command

    The STC3x measures the concentration of binary gas mixtures. It is
    important to note that the STC3x is not selective for gases, and it assumes
    that the binary gas is set correctly. The sensor can only give a correct
    concentration value when only the gases set with this command are present.
    When the system is reset, or wakes up from sleep mode, the sensor goes back
    to default mode, in which no binary gas is selected. This means that the
    binary gas must be reconfigured. When no binary gas is selected (default
    mode) the concentration measurement will return undefined results. This
    allows to detect unexpected sensor interruption (e.g. due to temporary
    power loss) and consequently reset the binary gas to the appropriate
    mixture.
    """

    def __init__(self, binary_gas):
        """
        Constructor.

        :param int binary_gas:
            See section 3.3.2 in the corresponding datasheet for a list of
            available binary gases. See :py:class:`Stc31BinaryGas`
        """
        super(Stc3xI2cCmdSetBinaryGas, self).__init__(
            command=0x3615,
            tx_data=b"".join([pack(">H", binary_gas)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdSetRelativeHumidity(Stc3xI2cCmdBase):
    """
    Set Relative Humidity I²C Command

    As mentioned in section 5.1 of the datasheet, the measurement principle of
    the concentration measurement is dependent on the humidity of the gas. With
    the set relative humidity command, the sensor uses internal algorithms to
    compensate the concentration results. When no value is written to the
    sensor after a soft reset, wake-up or power-up, a relative humidity of 0%
    is assumed. The value written to the sensor is used until a new value is
    written to the sensor
    """

    def __init__(self, relative_humidity_percent):
        """
        Constructor.

        :param float relative_humidity_percent: Relative humidity conditions.
        """
        super(Stc3xI2cCmdSetRelativeHumidity, self).__init__(
            command=0x3624,
            tx_data=b"".join([pack(">H", Stc3xRelativeHumidityConditionPercent(
                relative_humidity_percent).ticks)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdSetTemperature(Stc3xI2cCmdBase):
    """
    Set Temperature I²C Command

    The concentration measurement requires a compensation of temperature. Per
    default, the sensor uses the internal temperature sensor to compensate the
    concentration results. However, when using the SHTxx, it is recommended to
    also use its temperature value, because it is more accurate. When no value
    is written to the sensor after a soft reset, wake-up or power-up, the
    internal temperature signal is used. The value written to the sensor is
    used until a new value is written to the sensor.
    """

    def __init__(self, temperature_degree_celsius):
        """
        Constructor.

        :param float temperature_degree_celsius: Temperature conditions.
        """
        super(Stc3xI2cCmdSetTemperature, self).__init__(
            command=0x361E,
            tx_data=b"".join([pack(">H", Stc3xTemperatureConditionDegC(
                temperature_degree_celsius).ticks)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdSetPressure(Stc3xI2cCmdBase):
    """
    Set Pressure I²C Command

    A pressure value can be written into the sensor, for density compensation
    of the gas concentration measurement. It is recommended to set the pressure
    level, if it differs significantly from 1013mbar. Pressure compensation is
    valid from 600mbar to 1200mbar. When no value is written to the sensor
    after a soft reset, wake-up or power-up, a pressure of 1013mbar is assumed.
    The value written is used until a new value is written to the sensor.
    """

    def __init__(self, absolue_pressure):
        """
        Constructor.

        :param int absolue_pressure:
            Ambient pressure in mbar (milli-bars)
        """
        super(Stc3xI2cCmdSetPressure, self).__init__(
            command=0x362F,
            tx_data=b"".join([pack(">H", int(absolue_pressure))]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdMeasureGasConcentration(Stc3xI2cCmdBase):
    """
    Measure Gas Concentration I²C Command

    The measurement of gas concentration is done in one measurement in a single
    shot, and takes less than 66ms. When measurement data is available, it can
    be read out by sending an I2C read header and reading out the data from the
    sensor. If no measurement data is available yet, the sensor will respond
    with a NACK on the I2C read header. In case the ‘Set temperature command’
    has been used prior to the measurement command, the temperature value given
    out by the STC3x will be that one of the ‘Set temperature command’. When
    the ‘Set temperature command’ has not been used, the internal temperature
    value can be read out. During product development it is recommended to
    compare the internal temperature value of the STC3x and the temperature
    value of the SHTxx, to check whether both sensors are properly thermally
    coupled. The values must be within 0.7°C.

    .. note:: The Gas concentration is a 16-bit unsigned integer. The
              temperature and byte 7 and 8 don’t need to be read out. The read
              sequence can be aborted after any byte by a NACK and a STOP
              condition. The measurement command should not be triggered more
              often than once a second.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdMeasureGasConcentration, self).__init__(
            command=0x3639,
            tx_data=None,
            rx_length=6,
            read_delay=0.07,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - gas_concentration (:py:class:sensirion_i2c_stc.stc3x.response_types.Stc3xGasConcentration)
              Gas concentration response object
            - temperature (:py:class:sensirion_i2c_stc.stc3x.reasponse_types.Stc3xTemperature)
              Temperature response object.
        :rtype: tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Stc3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        gas_ticks = int(unpack(">H", checked_data[0:2])[0])  # uint16
        temperature_ticks = int(unpack(">H", checked_data[2:4])[0])  # uint16
        return Stc3xGasConcentration(gas_ticks), Stc3xTemperature(
            temperature_ticks)


class Stc3xI2cCmdForcedRecalibration(Stc3xI2cCmdBase):
    """
    Forced Recalibration I²C Command

    Forced recalibration (FRC) is used to improve the sensor output with a
    known reference value. See the Field Calibration Guide for more details. If
    no argument is given, the sensor will assume a default value of 0 vol%.
    This command will trigger a concentration measurement as described in 3.3.6
    of the datasheet and therefore it will take the same measurement time.
    """

    def __init__(self, reference_concentration_vol_percent):
        """
        Constructor.

        :param int reference_concentration_vol_percent: Reference concentration
        """
        super(Stc3xI2cCmdForcedRecalibration, self).__init__(
            command=0x3661,
            tx_data=b"".join([pack(">H", Stc3xReferenceConcentration(
                reference_concentration_vol_percent).ticks)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.066,
        )


class Stc3xI2cCmdEnableAutomaticSelfCalibration(Stc3xI2cCmdBase):
    """
    Enable Automatic Self Calibration I²C Command

    Enable the automatic self-calibration (ASC). The sensor can run in
    automatic self-calibration mode. This mode will enhance the accuracy for
    applications where the target gas is not present for the majority of the
    time. See the Field Calibration Guide for more details. This feature can be
    enabled or disabled by using the commands as shown below. The automatic
    self-calibration is optimized for a gas concentration measurement interval
    of 1s. Substantially different measurement intervals may decrease the
    self-calibration performance. The default state is disabled. Automatic
    self-calibration in combination with sleep mode requires a specific
    sequence of steps. See section 3.3.9 in the datasheet for more detailed
    instructions

    .. note:: The sensor will apply automatic self-calibration
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdEnableAutomaticSelfCalibration, self).__init__(
            command=0x3FEF,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdDisableAutomaticSelfCalibration(Stc3xI2cCmdBase):
    """
    Disable Automatic Self Calibration I²C Command

    Disable the automatic self-calibration (ASC). The sensor can run in
    automatic self-calibration mode. This mode will enhance the accuracy for
    applications where the target gas is not present for the majority of the
    time. See the Field Calibration Guide for more details. This feature can be
    enabled or disabled by using the commands as shown below. The default state
    is disabled.

    .. note:: The sensor will not apply automatic self-calibration. This is the
              default state of the sensor.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdDisableAutomaticSelfCalibration, self).__init__(
            command=0x3F6E,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdPrepareReadState(Stc3xI2cCmdBase):
    """
    Prepare Read State I²C Command

    The sensor will prepare its current state to be read out.

    .. note:: See section 3.3.9 of the datasheet for detailed instructions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdPrepareReadState, self).__init__(
            command=0x3752,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdGetSensorState(Stc3xI2cCmdBase):
    """
    Get Sensor State I²C Command

    Read out the sensor state.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdGetSensorState, self).__init__(
            command=0xE133,
            tx_data=None,
            rx_length=45,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: Current sensor state
        :rtype: list(int)
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Stc3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        state = [int(ii) for ii in
                 unpack(">{}B".format(len(checked_data[0:30]) // 1),
                        checked_data[0:30])]  # list(uint8)
        return state


class Stc3xI2cCmdSetSensorState(Stc3xI2cCmdBase):
    """
    Set Sensor State I²C Command

    Write the sensor state as read out earlier.
    """

    def __init__(self, state):
        """
        Constructor.

        :param list(int) state: Current sensor state
        """
        super(Stc3xI2cCmdSetSensorState, self).__init__(
            command=0xE133,
            tx_data=b"".join([pack(">{}B".format(len(state)), *state)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.0,
        )


class Stc3xI2cCmdApplyState(Stc3xI2cCmdBase):
    """
    Apply State I²C Command

    The sensor will apply the written state data.

    .. note:: See section 3.3.9 of the datasheet for detailed instructions.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdApplyState, self).__init__(
            command=0x3650,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdSelfTest(Stc3xI2cCmdBase):
    """
    Self Test I²C Command

    The sensor will run an on-chip self-test. A successful self-test will
    return zero. The 16-bit result of a sensor self-test is a combination of
    possible error states, encoded as bits (starting with lsb).
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdSelfTest, self).__init__(
            command=0x365B,
            tx_data=None,
            rx_length=3,
            read_delay=0.022,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: Self test result. Error code or 0x0000 on success.
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Stc3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        self_test_output = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return self_test_output


class Stc3xI2cCmdEnterSleepMode(Stc3xI2cCmdBase):
    """
    Enter Sleep Mode I²C Command

    Put sensor into sleep mode. In sleep mode the sensor uses the minimum
    amount of current. The mode can only be entered from idle mode, i.e. when
    the sensor is not measuring. This mode is particularly useful for battery
    operated devices. To minimize the current in this mode, the complexity of
    the sleep mode circuit has been reduced as much as possible, which is
    mainly reflected by the way the sensor exits the sleep mode. The sleep
    command can be sent after the result have been read out and the sensor is
    in idle mode. The sensor exits the sleep mode and enters the idle mode when
    it receives the valid I2C address and a write bit (‘0’). Note that the I2C
    address is not acknowledged. It is possible to poll the sensor to see
    whether the sensor has received the address and has woken up. This takes
    maximum 12ms.

    .. note:: Only available in idle mode
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdEnterSleepMode, self).__init__(
            command=0x3677,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Stc3xI2cCmdPrepareProductIdentifier(Stc3xI2cCmdBase):
    """
    Prepare Product Identifier I²C Command

    Prepare for reading the product identifier and sensor serial number.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdPrepareProductIdentifier, self).__init__(
            command=0x367C,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.0,
        )


class Stc3xI2cCmdReadProductIdentifier(Stc3xI2cCmdBase):
    """
    Read Product Identifier I²C Command

    Read the product identifier and sensor serial number.

    .. note:: Make sure to call 'prepare product identifier' immediately
              before.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Stc3xI2cCmdReadProductIdentifier, self).__init__(
            command=0xE102,
            tx_data=None,
            rx_length=18,
            read_delay=0.01,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - product_number (int) -
              32-bit unique product and revision number. The number is listed
              below: STC31: 0x08010301
            - serial_number (unsigned long long) 64-bit unique serial number
        :rtype: tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Stc3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        product_number = int(unpack(">I", checked_data[0:4])[0])  # uint32
        serial_number = int(unpack(">Q", checked_data[4:12])[0])  # uint64
        return product_number, serial_number
