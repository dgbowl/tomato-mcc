import psutil

if psutil.WINDOWS:
    from .win import Device, DriverInterface
elif psutil.LINUX:
    from .lin import Device, DriverInterface

__all__ = ["Device", "DriverInterface"]
