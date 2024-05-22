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


def walktree(buffer: bytes):
    buffersize = len(buffer)
    pointer = 0
    while pointer < buffersize:
        tag = buffer[pointer]

        while True:
            if tag == TAG_End:
                pointer += 1
                # print("TAG_End")
                break

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
                print(name)
                break
            if tag == TAG_String:
                value, pointer = getString(buffer, pointer)
                print(name, value)
                break
            if tag == TAG_List:
                type = buffer[pointer]
                pointer += 1
                items, pointer = getInt(buffer, pointer, 4)
                data = ""
                if type == 0x00:
                    print("TAG_List", type, name, data)
                elif type == TAG_Int:
                    data, pointer = getList(buffer, pointer, items, lambda b, p: getInt(b, p, 4))
                    print(name, data)
                elif type == TAG_Float:
                    data, pointer = getList(buffer, pointer, items, getFloat)
                    print(name, data)
                elif type == TAG_Double:
                    data, pointer = getList(buffer, pointer, items, getDouble)
                    print(name, data)
                elif type == TAG_String:
                    data, pointer = getList(buffer, pointer, items, getString)
                    print(name, data)
                else:
                    print("TAG_List", type, name, data)
                break
            if tag == TAG_Compound:
                print(name)
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

            print("debug", pointer, buffer[pointer:pointer].hex(), buffer[pointer - 10 : pointer + 10].hex())
            return


def main():
    for filespec in sys.argv[1:]:
        if not os.path.isfile(filespec):
            print(f"{filespec} is not a valid file")
            continue

        with gzip.open(filespec, "rb") as fd:
            buffer = fd.read()
            print(fd.name, len(buffer), "bytes")
            fd.close()
            walktree(buffer)
            print()


if __name__ == "__main__":
    main()
