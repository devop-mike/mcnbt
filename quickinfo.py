#!/usr/bin/python3

import sys
import os
import gzip
import datetime


def findget(buffer: bytes, hex: str, size: int):
    pattern = bytes.fromhex(hex)
    ind = buffer.find(pattern)
    if ind > -1:
        valstart = ind + len(pattern)
        valend = valstart + size
        return buffer[valstart:valend]
    return bytes()


def getLevelName(buffer: bytes):
    pattern = bytes.fromhex("4C6576656C4E616D65")
    ind = buffer.find(pattern)
    if ind > -1:
        valstart = ind + len(pattern)
        valend = valstart + 2
        size = int.from_bytes(buffer[valstart:valend])
        valstart = valend
        valend = valstart + size
        return buffer[valstart:valend]
    return bytes()


def main():
    for filespec in sys.argv[1:]:
        if not os.path.isfile(filespec):
            print(f"{filespec} is not a valid file")
            continue

        with gzip.open(filespec, "rb") as fd:
            buffer = fd.read()
            print(fd.name, len(buffer), "bytes")
            fd.close()

            subbuf = getLevelName(buffer)
            if subbuf:
                print("Name", subbuf.decode())

            subbuf = findget(buffer, "04000744617954696d65", 8)
            if subbuf:
                val = int.from_bytes(subbuf, signed=True)
                day = int(val / 24000) + 1
                pid = val % 24000
                hour = int(pid / 1000) + 6
                min = int(pid % 1000 / 16.666)
                # print("DayTime", val)
                print(f"Day {day} Time {hour:02}:{min:02}")

            subbuf = findget(buffer, "04000a4c617374506c61796564", 8)
            if subbuf:
                val = int.from_bytes(subbuf, signed=True)
                print("LastPlayed", datetime.datetime.fromtimestamp(val / 1000).isoformat())

            subbuf = findget(buffer, "04000473656564", 8)  # seed
            if subbuf:
                val = int.from_bytes(subbuf, signed=True)
                print(f"Seed {val:-20} Hex {subbuf.hex()}")

            subbuf = findget(buffer, "04000a52616e646f6d53656564", 8)  # RandomSeed
            if subbuf:
                val = int.from_bytes(subbuf, signed=True)
                print(f"Seed {val:-20} Hex {subbuf.hex()}")

            print()


if __name__ == "__main__":
    main()
