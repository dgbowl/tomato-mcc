from typing import Any
from types import ModuleType
from tomato.driverinterface_2_1 import ModelInterface, ModelDevice, Attr
from tomato.driverinterface_2_1.decorators import coerce_val
from tomato.driverinterface_2_1.types import Val
import psutil
import sys
import importlib
from datetime import datetime
import xarray as xr
import pint
import time
from functools import wraps

pint.set_application_registry(pint.UnitRegistry(autoconvert_offset_to_baseunit=True))
ul: ModuleType = None
enums: ModuleType = None

READ_DELAY = 0.01


def read_delay(func):
    @wraps(func)
    def wrapper(self: ModelDevice, **kwargs):
        if time.perf_counter() - self.last_action < READ_DELAY:
            time.sleep(READ_DELAY)
        return func(self, **kwargs)

    return wrapper


class DriverInterface(ModelInterface):
    idle_measurement_interval = 1.0

    def __init__(self, settings=None):
        super().__init__(settings)
        if "dllpath" not in self.settings:
            raise RuntimeError(
                "Cannot instantiate tomato-mcc without supplying a 'dllpath'."
            )
        if psutil.WINDOWS:
            sys.path.append(self.settings["dllpath"])

        global ul
        ul = importlib.import_module("mcculw.ul")
        global enums
        enums = importlib.import_module("mcculw.enums")

    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)


class Device(ModelDevice):
    board_num: int
    channel: int
    last_action: float

    def __init__(self, driver: ModelInterface, key: tuple[str, str], **kwargs: dict):
        self.board_num = int(key[0])
        self.channel = int(key[1])
        self.last_action = time.perf_counter()
        super().__init__(driver, key, **kwargs)

    @property
    @read_delay
    def temperature(self) -> pint.Quantity:
        try:
            t = ul.t_in(self.board_num, self.channel, enums.TempScale.CELSIUS)
        except ul.ULError as e:
            raise AttributeError(str(e)) from e
        return pint.Quantity(t, "celsius")

    def attrs(self, **kwargs: dict) -> dict[str, Attr]:
        attrs_dict = {
            "temperature": Attr(type=pint.Quantity, units="celsius", status=True),
        }
        return attrs_dict

    def capabilities(self, **kwargs: dict) -> set:
        capabs = {"measure_temperature"}
        return capabs

    def do_measure(self, **kwargs: dict) -> None:
        coords = {"uts": (["uts"], [datetime.now().timestamp()])}
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
    def set_attr(self, attr: str, val: Any, **kwargs: dict) -> Val:
        pass
