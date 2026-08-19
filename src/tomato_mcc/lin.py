import logging
import time
from datetime import datetime
from datetime import timezone as tz
from functools import wraps
from typing import Any, Union

import pint
import uldaq
import xarray as xr
from tomato.driverinterface_2_1 import Attr, ModelDevice, ModelInterface
from tomato.driverinterface_2_1.decorators import coerce_val

pint.set_application_registry(pint.UnitRegistry(autoconvert_offset_to_baseunit=True))
logger = logging.getLogger(__name__)

READ_DELAY = 0.05


def read_delay(func):
    @wraps(func)
    def wrapper(self: "Device", **kwargs):
        if time.perf_counter() - self.last_action < READ_DELAY:
            time.sleep(READ_DELAY)
        return func(self, **kwargs)

    return wrapper


class DriverInterface(ModelInterface):
    idle_measurement_interval = 1.0

    def __init__(self, settings=None):
        super().__init__(settings)

    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)


class Device(ModelDevice):
    board_num: int
    channel: int
    last_action: float
    daq: Union[uldaq.DaqDevice, None] = None  # noqa: FA100

    def __init__(self, driver: DriverInterface, key: tuple[str, str], **kwargs: dict):
        self.board_num = int(key[0])
        self.channel = int(key[1])
        self.last_action = time.perf_counter()
        super().__init__(driver, key, **kwargs)
        devices = uldaq.get_daq_device_inventory(uldaq.InterfaceType.USB)
        self.daq = uldaq.DaqDevice(devices[self.board_num])
        self.daq.connect()
        cfg = self.daq.get_ai_device().get_config()
        tc_type = self.driver.settings.get("tc_type", {}).get(f"{self.channel}", "J")
        par = getattr(uldaq.TcType, tc_type, uldaq.TcType.K)
        if cfg.get_chan_tc_type(self.channel) != par:
            logger.info("setting TC type to '%s'", repr(par))
            cfg.set_chan_tc_type(self.channel, par)

    @property
    @read_delay
    def temperature(self) -> pint.Quantity:
        assert self.daq is not None
        try:
            ai = self.daq.get_ai_device()
            t = ai.t_in(self.channel, uldaq.TempScale.CELSIUS)
        except uldaq.ul_exception.ULException as e:
            raise AttributeError(str(e)) from e
        return pint.Quantity(t, "celsius")  # ty: ignore[invalid-return-type]

    def attrs(self, **kwargs: dict) -> dict[str, Attr]:
        attrs_dict = {
            "temperature": Attr(type=pint.Quantity, units="celsius", status=True),
        }
        return attrs_dict

    def capabilities(self, **kwargs: dict) -> set:
        capabs = {"measure_temperature"}
        return capabs

    def do_measure(self, **kwargs: dict) -> None:
        coords = {"uts": (["uts"], [datetime.now(tz.utc).timestamp()])}
        temperature = self.temperature
        data_vars = {
            "temperature": (["uts"], [temperature.m], {"units": str(temperature.u)}),
        }
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords=coords,
        )

    def get_attr(self, attr: str, **kwargs: dict) -> pint.Quantity:
        if attr not in self.attrs():
            raise AttributeError(f"Unknown attr: {attr!r}")
        return getattr(self, attr)

    @coerce_val
    def set_attr(self, attr: str, val: Any, **kwargs: dict) -> None:
        pass

    def reset(self, do_run: bool = True, **kwargs) -> None:
        try:
            if do_run is False and self.daq is not None:
                self.daq.disconnect()
                self.daq = None
        except uldaq.ul_exception.ULException:
            pass
        super().reset()
