# tomato-mcc
`tomato` driver for MCC DAQ temperature readers (ME-Redlab, Digilent).

This driver is based on the [`mcculw`](https://github.com/mccdaq/mcculw) library, and is currently Windows-only. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Installation
1. Install DAQami, make sure you know the `dllpath` where `cbw32.dll` and `cbw64.dll` can be found. Normally, this is `"C:\Program Files (x86)\Measurement Computing\DAQ"`.
2. Install InstaCal, configure your board selecting appropriate thermocouple type. This will generate `CB.CFG`.
3. Pass the `dllpath` as `settings['dllpath']` to the driver.

## Supported functions

### Capabilities
- `measure_temperature` which measures the temperature on a given board (`address`) and `channel`

### Attributes
- `temperature` which is the current temperature, `pint.Quantity(float, "degC")`

## Contributors

- Peter Kraus
