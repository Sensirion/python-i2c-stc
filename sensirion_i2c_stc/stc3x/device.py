# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

from sensirion_i2c_driver import I2cDevice

from .commands import Stc3xI2cCmdPrepareProductIdentifier, \
    Stc3xI2cCmdReadProductIdentifier, Stc3xI2cCmdSetBinaryGas, \
    Stc3xI2cCmdSetRelativeHumidity, Stc3xI2cCmdSetTemperature, \
    Stc3xI2cCmdSetPressure, Stc3xI2cCmdMeasureGasConcentration, \
    Stc3xI2cCmdForcedRecalibration, Stc3xI2cCmdEnableAutomaticSelfCalibration, \
    Stc3xI2cCmdDisableAutomaticSelfCalibration, Stc3xI2cCmdPrepareReadState, \
    Stc3xI2cCmdGetSensorState, Stc3xI2cCmdSetSensorState, \
    Stc3xI2cCmdApplyState, Stc3xI2cCmdSelfTest, Stc3xI2cCmdEnterSleepMode


class Stc3xI2cDevice(I2cDevice):
    """
    STC3x I²C device class to allow executing I²C commands.
    """

    def __init__(self, connection, slave_address=0x29):
        """
        Constructs a new STC3x I²C device.

        :param ~sensirion_i2c_driver.connection.I2cConnection connection:
            The I²C connection to use for communication.
        :param byte slave_address:
            The I²C slave address, defaults to 0x29.
        """
        super(Stc3xI2cDevice, self).__init__(connection, slave_address)

    def read_product_identifier(self):
        """
        Read the product identifier and sensor serial number.

        :return: The product number and serial number.
        :rtype: tuple
        """
        self.execute(Stc3xI2cCmdPrepareProductIdentifier())
        return self.execute(Stc3xI2cCmdReadProductIdentifier())

    def set_bianry_gas(self, binary_gas):
        """
        Set Binary Gas

        The STC3x measures the concentration of binary gas mixtures. It is
        important to note that the STC3x is not selective for gases, and it
        assumes that the binary gas is set correctly. The sensor can only give
        a correct concentration value when only the gases set with this command
        are present. When the system is reset, or wakes up from sleep mode, the
        sensor goes back to default mode, in which no binary gas is selected.
        This means that the binary gas must be reconfigured. When no binary gas
        is selected (default mode) the concentration measurement will return
        undefined results. This allows to detect unexpected sensor interruption
        (e.g. due to temporary power loss) and consequently reset the binary
        gas to the appropriate mixture.

        :param ~sensirion_i2c_stc.stc3x.data_types.Stc31BinaryGas binary_gas:
            See section 3.3.2 in the corresponding datasheet for a list of
            available binary gases.
        """
        return self.execute(Stc3xI2cCmdSetBinaryGas(binary_gas))

    def set_relative_humidity(self, relative_humidity_percent):
        """
        Set Relative Humidity

        As mentioned in section 5.1 of the datasheet, the measurement principle
        of the concentration measurement is dependent on the humidity of the
        gas. With the set relative humidity command, the sensor uses internal
        algorithms to compensate the concentration results. When no value is
        written to the sensor after a soft reset, wake-up or power-up, a
        relative humidity of 0% is assumed. The value written to the sensor is
        used until a new value is written to the sensor

        :param float relative_humidity_percent: Relative humidity conditions.
        """
        return self.execute(
            Stc3xI2cCmdSetRelativeHumidity(relative_humidity_percent))

    def set_temperature(self, temperature_degree_celsius):
        """
        Set Temperature

        The concentration measurement requires a compensation of temperature.
        Per default, the sensor uses the internal temperature sensor to
        compensate the concentration results. However, when using the SHTxx,
        it is recommended to also use its temperature value, because it is more
        accurate. When no value is written to the sensor after a soft reset,
        wake-up or power-up, the internal temperature signal is used. The value
        written to the sensor is used until a new value is written to the
        sensor.

        :param float temperature_degree_celsius: Temperature conditions.
        """
        return self.execute(
            Stc3xI2cCmdSetTemperature(temperature_degree_celsius))

    def set_pressure(self, absolute_pressure):
        """
        Set Pressure

        A pressure value can be written into the sensor, for density
        compensation of the gas concentration measurement. It is recommended to
        set the pressure level, if it differs significantly from 1013mbar.
        Pressure compensation is valid from 600mbar to 1200mbar. When no value
        is written to the sensor after a soft reset, wake-up or power-up, a
        pressure of 1013mbar is assumed. The value written is used until a new
        value is written to the sensor.

        :param int absolute_pressure: Ambient pressure condition in mbar
            (milli-bars)
        """
        return self.execute(Stc3xI2cCmdSetPressure(absolute_pressure))

    def measure_gas_concentration(self):
        """
        Measure Gas Concentration

        The measurement of gas concentration is done in one measurement in a
        single shot, and takes less than 66ms. When measurement data is
        available, it can be read out by sending an I2C read header and reading
        out the data from the sensor. If no measurement data is available yet,
        the sensor will respond with a NACK on the I2C read header. In case the
        ‘Set temperature command’ has been used prior to the measurement
        command, the temperature value given out by the STC3x will be that one
        of the ‘Set temperature command’. When the ‘Set temperature command’
        has not been used, the internal temperature value can be read out.
        During product development it is recommended to compare the internal
        temperature value of the STC3x and the temperature value of the SHTxx,
        to check whether both sensors are properly thermally coupled. The
        values must be within 0.7°C.

        .. note:: The Gas concentration is a 16-bit unsigned integer. The
                  temperature and byte 7 and 8 don’t need to be read out. The
                  read sequence can be aborted after any byte by a NACK and a
                  STOP condition. The measurement command should not be
                  triggered more often than once a second.

        :return:
            - gas_concentration (:py:class:sensirion_i2c_stc.stc3x.response_types.Stc3xGasConcentration)
              Gas concentration response object
            - temperature (:py:class:sensirion_i2c_stc.stc3x.reasponse_types.Stc3xTemperature)
              Temperature response object.
        :rtype: tuple
        """
        return self.execute(Stc3xI2cCmdMeasureGasConcentration())

    def perform_forced_recalibration(self, target_concentration):
        """
        Forced Recalibration

        Forced recalibration (FRC) is used to improve the sensor output with a
        known reference value. See the Field Calibration Guide for more
        details. If no argument is given, the sensor will assume a default
        value of 0 vol%. This command will trigger a concentration measurement
        as described in 3.3.6 of the datasheet and therefore it will take the
        same measurement time.

        :param int target_concentration: Target concentration in vol%.
        """
        return self.execute(
            Stc3xI2cCmdForcedRecalibration(target_concentration))

    def enable_automatic_self_calibration(self):
        """
        Enable Automatic Self Calibration

        Enable the automatic self-calibration (ASC). The sensor can run in
        automatic self-calibration mode. This mode will enhance the accuracy
        for applications where the target gas is not present for the majority
        of the time. See the Field Calibration Guide for more details. This
        feature can be enabled or disabled by using the commands as shown
        below. The automatic self-calibration is optimized for a gas
        concentration measurement interval of 1s. Substantially different
        measurement intervals may decrease the self-calibration performance.
        The default state is disabled. Automatic self-calibration in
        combination with sleep mode requires a specific sequence of steps.
        See section 3.3.9 in the datasheet for more detailed instructions

        .. note:: The sensor will apply automatic self-calibration
        """
        return self.execute(Stc3xI2cCmdEnableAutomaticSelfCalibration())

    def disable_automatic_self_calibration(self):
        """
        Disable Automatic Self Calibration

        Disable the automatic self-calibration (ASC). The sensor can run in
        automatic self-calibration mode. This mode will enhance the accuracy
        for applications where the target gas is not present for the majority
        of the time. See the Field Calibration Guide for more details. This
        feature can be enabled or disabled by using the commands as shown
        below. The default state is disabled.

        .. note:: The sensor will not apply automatic self-calibration. This is
                  the default state of the sensor.
        """
        return self.execute(Stc3xI2cCmdDisableAutomaticSelfCalibration())

    def read_state(self):
        """
        Read out the sensor state.

        .. note:: See section 3.3.9 of the datasheet for detailed instructions.

        :return: Current sensor state
        :rtype: list(int)
        """
        self.execute(Stc3xI2cCmdPrepareReadState())
        return self.execute(Stc3xI2cCmdGetSensorState())

    def apply_state(self, state):
        """
        Write the sensor state as read out earlier.

        .. note:: See section 3.3.9 of the datasheet for detailed instructions.

        :param list(int) state: Previously sensor state to set and apply.

        """
        self.execute(Stc3xI2cCmdSetSensorState(state))
        return self.execute(Stc3xI2cCmdApplyState())

    def perform_self_test(self):
        """
        Self Test

        The sensor will run an on-chip self-test. A successful self-test will
        return zero. The 16-bit result of a sensor self-test is a combination
        of possible error states, encoded as bits (starting with lsb).

        :return: 0 means no malfunction detected
        :rtype: int
        """
        return self.execute(Stc3xI2cCmdSelfTest())

    def enable_sleep_mode(self):
        """
        Enter Sleep Mode

        Put sensor into sleep mode. In sleep mode the sensor uses the minimum
        amount of current. The mode can only be entered from idle mode, i.e.
        when the sensor is not measuring. This mode is particularly useful for
        battery operated devices. To minimize the current in this mode, the
        complexity of the sleep mode circuit has been reduced as much as
        possible, which is mainly reflected by the way the sensor exits the
        sleep mode. The sleep command can be sent after the result have been
        read out and the sensor is in idle mode. The sensor exits the sleep
        mode and enters the idle mode when it receives the valid I2C address
        and a write bit (‘0’). Note that the I2C address is not acknowledged.
        It is possible to poll the sensor to see whether the sensor has
        received the address and has woken up. This takes maximum 12ms.

        .. note:: Only available in idle mode
        """
        return self.execute(Stc3xI2cCmdEnterSleepMode())
