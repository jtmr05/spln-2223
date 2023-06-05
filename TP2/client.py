#!/usr/bin/env python

import pickle
import socket
import argparse
import io

PORT: int = 9000
BUFFER_SIZE: int = 1024


def as_bytes(s: str) -> bytes:
    return s.encode('utf-8')


def from_bytes(b: bytes) -> str:
    return b.decode('utf-8')


def main():
    parser = argparse.ArgumentParser(
        prog='whisper_client',
        description='Transcribe an audio file'
    )

    parser.add_argument(
        '--lang', '-l',
        help="Define the audio language",
        default=None, required=False
    )
    parser.add_argument('--task', '-t', help="Define the task", default=None, required=False)
    parser.add_argument('filename')

    args: dict[str, str] = vars(parser.parse_args())
    print(args)
    args = pickle.dumps(args)

    request_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request_socket.sendto(args, ('', PORT))

    msg_size = pickle.loads(request_socket.recv(BUFFER_SIZE))
    recv_size = 0
    result = io.StringIO()
    while recv_size < msg_size:
        result.write(from_bytes(request_socket.recv(BUFFER_SIZE)))
        recv_size += BUFFER_SIZE

    print(result.getvalue())

    try:
        request_socket.close()
    finally:
        pass


if __name__ == '__main__':
    main()
