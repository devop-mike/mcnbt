#!/usr/bin/python3

import sys
import os
import gzip
import struct

# tag ids
TAG_End = 0x00
TAG_Byte = 0x01
TAG_Short = 0x02
TAG_Int = 0x03
TAG_Long = 0x04
TAG_Float = 0x05
TAG_Double = 0x06
TAG_Byte_Array = 0x07
TAG_String = 0x08
TAG_List = 0x09
TAG_Compound = 0x0A
TAG_Int_Array = 0x0B
TAG_Long_Array = 0x0C


def getString(buffer: bytes, pointer: int):
    start = pointer
    end = start + 2
    size = int.from_bytes(buffer[start:end])
    if size:
        start = end
        end = end + size
        return buffer[start:end].decode(), end
    return "", end


def getInt(buffer: bytes, pointer: int, numbytes: int):
    start = pointer
    end = start + numbytes
    return int.from_bytes(buffer[start:end], signed=True), end


def getFloat(buffer: bytes, pointer: int):
    start = pointer
    end = start + 4
    val = struct.unpack(">f", buffer[start:end])
    return val[0], end


def getDouble(buffer: bytes, pointer: int):
    start = pointer
    end = start + 8
    val = struct.unpack(">d", buffer[start:end])
    return val[0], end


def getHex(buffer: bytes, pointer: int, size: int):
    start = pointer
    end = start + size
    return buffer[start:end].hex(), end


def getList(buffer: bytes, pointer: int, items: int, func: callable):
    data = []
    while items:
        value, pointer = func(buffer, pointer)
        data.append(value)
        items -= 1

    return data, pointer


def debugdata(buffer: bytes, pointer: int):
    if pointer < 0:
        pointer = 0
    end = pointer + 32
    asstring = buffer[pointer:end].hex(" ")
    return f"({pointer:-5}):    {asstring}"


def getListPayload(buffer: bytes, pointer: int, type: int, items: int):
    func = lambda b, p: ("getListPayload", p)
    if type == TAG_Int:
        func = lambda b, p: getInt(b, p, 4)
    if type == TAG_Long:
        func = lambda b, p: getInt(b, p, 8)
    if type == TAG_Float:
        func = getFloat
    if type == TAG_Double:
        func = getDouble
    if type == TAG_String:
        func = getString
    if type == TAG_Compound:
        func = lambda b, p: ("getCompoundPayload", getCompoundPayload(b, p))

    return getList(buffer, pointer, items, func)


def getCompoundPayload(buffer: bytes, pointer: int):
    tagcount = 0
    while pointer < len(buffer):
        tag = buffer[pointer]
        tagcount += 1
        while True:
            if tag == TAG_End:
                # print(f"(TAG {tag}/{tagcount})", debugdata(buffer, pointer))
                return pointer + 1

            name, pointer = getString(buffer, pointer + 1)
            if tag == TAG_Byte:
                value, pointer = getInt(buffer, pointer, 1)
                print(name, value)
                break
            if tag == TAG_Short:
                value, pointer = getInt(buffer, pointer, 2)
                print(name, value)
                break
            if tag == TAG_Int:
                value, pointer = getInt(buffer, pointer, 4)
                print(name, value)
                break
            if tag == TAG_Long:
                value, pointer = getInt(buffer, pointer, 8)
                print(name, value)
                break
            if tag == TAG_Float:
                value, pointer = getFloat(buffer, pointer)
                print(name, value)
                break
            if tag == TAG_Double:
                value, pointer = getDouble(buffer, pointer)
                print(name, value)
                break
            if tag == TAG_Byte_Array:
                items, pointer = getInt(buffer, pointer, 4)
                data, pointer = getList(buffer, pointer, items, lambda b, p: getInt(b, p, 1))
                print(name, data)
                break
            if tag == TAG_String:
                value, pointer = getString(buffer, pointer)
                print(name, value)
                break
            if tag == TAG_List:
                type = buffer[pointer]
                items, pointer = getInt(buffer, pointer + 1, 4)
                data, pointer = getListPayload(buffer, pointer, type, items)
                print(name, data)
                break
            if tag == TAG_Compound:
                print(name)
                pointer = getCompoundPayload(buffer, pointer)
                break
            if tag == TAG_Int_Array:
                items, pointer = getInt(buffer, pointer, 4)
                data, pointer = getList(buffer, pointer, items, lambda b, p: getInt(b, p, 4))
                print(name, data)
                break
            if tag == TAG_Long_Array:
                items, pointer = getInt(buffer, pointer, 4)
                data, pointer = getList(buffer, pointer, items, lambda b, p: getInt(b, p, 8))
                print(name, data)
                break

            print("Unknown", tagcount)
            break
    return pointer


def main():
    for filespec in sys.argv[1:]:
        if not os.path.isfile(filespec):
            print(f"{filespec} is not a valid file")
            continue

        with gzip.open(filespec, "rb") as fd:
            buffer = fd.read()
            buffersize = len(buffer)
            print(fd.name, buffersize, "bytes")
            fd.close()
            pointer = getCompoundPayload(buffer, 0)
            print()


if __name__ == "__main__":
    main()
