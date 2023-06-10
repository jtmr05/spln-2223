import io
import typing
import socket


def as_bytes(s: str) -> bytes:
    return s.encode('utf-8')


def from_bytes(b: bytes) -> str:
    return b.decode('utf-8')


def annotate(src: typing.Any, *ansi_escape_codes: int) -> str:

    length: int = len(ansi_escape_codes)
    if length == 0:
        return str(src)

    str_buffer: io.StringIO = io.StringIO()

    str_buffer.write(f"\033[{ansi_escape_codes[0]}")
    for code in ansi_escape_codes[1:]:
        str_buffer.write(f";{code}")
    str_buffer.write(f"m{str(src)}\033[0m")

    return str_buffer.getvalue()


def read_reliably(s: socket.socket, size: int) -> bytes:
    buffer: bytearray = bytearray(size)
    view: memoryview = memoryview(buffer)
    i: int = 0
    while i < size:
        b_read: int = s.recv_into(view[i:], size - i)
        if b_read == 0:
            break
        i += b_read
    return bytes(buffer)


def write_reliably(s: socket.socket, buffer: typing.Union[bytearray, bytes], size: int) -> int:
    view: memoryview = memoryview(buffer)
    i: int = 0
    while i < size:
        b_sent: int = s.send(view[i:])
        if b_sent == 0:
            break
        i += b_sent
    return i
