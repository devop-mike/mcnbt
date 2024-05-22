#!/usr/bin/python3

import gzip
import sys
import struct


def getString(fd):
    size = int.from_bytes(fd.read(2))
    if size:
        return fd.read(size).decode()
    return ""


def getInt(fd, numbytes):
    return int.from_bytes(fd.read(numbytes), signed=True)


def getFloat(fd):
    val = struct.unpack("f", fd.read(4))
    return val[0]


def getDouble(fd):
    val = struct.unpack("d", fd.read(8))
    return val[0]


def walktree(buffer: bytes):
    badbyte = False
    indentstr = "   -"
    indent = 0
    while not badbyte:
        tagid = fd.read(1)
        if len(tagid) < 1:
            break
        tagbyte = tagid[0]
        while True:
            if tagbyte == 0x00:  # TAG_End
                indent -= 1
                break
            if tagbyte == 0x01:  # TAG_Byte
                name = getString(fd)
                value = getInt(fd, 1)
                print(indentstr * indent, name, value)
                break
            if tagbyte == 0x02:  # TAG_Short
                name = getString(fd)
                value = getInt(fd, 2)
                print(indentstr * indent, "TAG_Short", name, value)
                break
            if tagbyte == 0x03:  # TAG_Int
                name = getString(fd)
                value = getInt(fd, 4)
                print(indentstr * indent, name, value)
                break
            if tagbyte == 0x04:  # TAG_Long
                name = getString(fd)
                value = getInt(fd, 8)
                print(indentstr * indent, name, value)
                break
            if tagbyte == 0x05:  # TAG_Float
                name = getString(fd)
                value = getFloat(fd)
                print(indentstr * indent, "TAG_Float", name, value)
                break
            if tagbyte == 0x06:  # TAG_Double
                name = getString(fd)
                value = getDouble(fd)
                print(indentstr * indent, name, value)
                break
            if tagbyte == 0x07:  # TAG_Byte_Array
                name = getString(fd)
                items = getInt(fd, 4)
                value = fd.read(items).hex()
                print(indentstr * indent, "TAG_Byte_Array", name, items, value)
                break
            if tagbyte == 0x08:  # TAG_String
                name = getString(fd)
                value = getString(fd)
                print(indentstr * indent, name, value)
                break
            if tagbyte == 0x09:  # TAG_List
                name = getString(fd)
                type = fd.read(1)[0]
                items = getInt(fd, 4)
                data = ""
                if type == 0x00:
                    data = "nodata"
                elif type == 0x03:
                    data = fd.read(items * 4).hex()
                elif type == 0x05:
                    data = fd.read(items * 4).hex()
                elif type == 0x06:
                    data = fd.read(items * 8).hex()
                elif type == 0x08:
                    data = []
                    cnt = items
                    while cnt:
                        data.append(getString(fd))
                        cnt -= 1
                print(indentstr * indent, "TAG_List", name, type, items, data)
                break
            if tagbyte == 0x0A:  # TAG_Compound
                name = getString(fd)
                print(indentstr * indent, name)
                indent += 1
                break
            if tagbyte == 0x0B:  # TAG_Int_Array
                name = getString(fd)
                items = getInt(fd, 4)
                value = fd.read(items * 4).hex()
                print(indentstr * indent, "TAG_Int_Array", name, value)
                break
            if tagbyte == 0x0C:  # TAG_Long_Array
                name = getString(fd)
                items = getInt(fd, 4)
                value = fd.read(items * 8).hex()
                print(indentstr * indent, "TAG_Long_Array", name, value)
                break

            print("\nbad byte", tagid.hex(), fd.read(16).hex())
            badbyte = True
            break

        # print("")
    print("Endindent", indent)


def main():
    for filespec in sys.argv[1:]:
        if not os.path.isfile(filespec):
            print(f"{filespec} is not a valid file")
            continue

        with gzip.open(filespec, "rb") as fd:
            buffer = fd.read()
            print(fd.name, len(buffer), "bytes")
            fd.close()
            walktree()


if __name__ == "__main__":
    main()
