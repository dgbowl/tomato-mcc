from tomato_mcc import DriverInterface

if __name__ == "__main__":
    interface = DriverInterface(
        settings={
            "dllpath": r"C:\Program Files (x86)\Measurement Computing\DAQ",
            "tc_type": {
                "1": "K",
            },
        }
    )
    print(f"{interface.cmp_register(address='0', channel='1')=}")
    # print(f"{interface.cmp_register(address='0', channel='0')=}")
    cmp1 = interface.devmap[("0", "1")]
    print(f"{interface.settings=}")
    # cmp2 = interface.devmap[("0", "0")]
    for i in range(0, 5):
        print(f"{cmp1.temperature=}")
        # print(f"{cmp2.temperature=}")
        # time.sleep(0.0)
    # print(mcculw.enums)
