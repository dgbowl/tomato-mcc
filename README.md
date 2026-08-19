# tomato-mcc
`tomato` driver for MCC DAQ temperature readers (ME-Redlab, Digilent).

This driver is based on the [`mcculw`](https://github.com/mccdaq/mcculw) library for Windows, and the [`uldaq`](https://github.com/mccdaq/uldaq) library for Linux. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Installation
### Windows
1. Install DAQami, make sure you know the `dllpath` where `cbw32.dll` and `cbw64.dll` can be found. Normally, this is `"C:\Program Files (x86)\Measurement Computing\DAQ"`.
2. Install InstaCal, configure your board selecting appropriate thermocouple type. This will generate `CB.CFG`. **Note:** This needs to be done every time a new board is connected and the board numbers may change.
3. Pass the `dllpath` as `settings['dllpath']` to the driver.
4. Optionally, you can set thermocouple type per channel using `settings['tc_type'][<channel>]`.

### Linux
1. Install the `libuldaq` library, either from source or from your package manager.
2. Make sure you have the right permissions for access to the USB device. Usually this can be achieved by adding your user to the `adm` group.
3. Optionally, you can set thermocouple type per channel using `settings['tc_type'][<channel>]`.

## Supported functions

### Capabilities
- `measure_temperature` which measures the temperature on a given board (`address`) and `channel`

### Attributes
- `temperature` which is the current temperature, `pint.Quantity(float, "degC")`

## Contributors

- Peter Kraus
