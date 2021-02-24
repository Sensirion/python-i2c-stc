Quick Start
===========

SensorBridge Example
--------------------

Following example code shows how to use this driver with a Sensirion STC3x
connected to the computer using a `Sensirion SEK-SensorBridge`_. It is assumed,
that the sensor is plugged into port 1 of the SensorBridge and COM Port 1 is
used on the computer. The driver for the SensorBridge can be installed with

.. sourcecode:: bash

    pip install sensirion-shdlc-sensorbridge


.. sourcecode:: python

    import time

    from sensirion_i2c_driver import I2cConnection
    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
    from sensirion_shdlc_sensorbridge import SensorBridgePort, \
        SensorBridgeShdlcDevice, SensorBridgeI2cProxy

    from sensirion_i2c_stc import Stc3xI2cDevice
    from sensirion_i2c_stc.stc3x.data_types import Stc31BinaryGas

    # Connect to the SensorBridge with default settings:
    #  - baudrate:      460800
    #  - slave address: 0
    with ShdlcSerialPort(port='COM1', baudrate=460800) as port:
        bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("SensorBridge SN: {}".format(bridge.get_serial_number()))

        # Configure SensorBridge port 1 for STC3x
        bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=400e3)
        bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=3.3)
        bridge.switch_supply_on(SensorBridgePort.ONE)

        # Create STC3x device
        i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
        stc3x = Stc3xI2cDevice(I2cConnection(i2c_transceiver))

        # set binary gas
        stc3x.set_bianry_gas(Stc31BinaryGas.Co2InAirRange100)

        # Measure once per second
        while True:
            time.sleep(1)
            gas_concentration, temperature = stc3x.measure_gas_concentration()
            # use default formatting for printing output:
            print("{}, {}".format(gas_concentration, temperature))
            # custom printing of attributes:
            print(
                "{:0.2f} vol% ({} ticks), {:0.2f} °F ({} ticks)".format(
                    gas_concentration.vol_percent, gas_concentration.ticks,
                    temperature.degrees_fahrenheit, temperature.ticks))

.. _Sensirion SEK-SensorBridge: https://www.sensirion.com/sensorbridge/
