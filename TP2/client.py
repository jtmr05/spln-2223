#!/usr/bin/env python

import argparse
import os
import pickle
import socket
import sys
import time

import utils as ut
import config

Socket = socket.socket

TIMEOUT: float = 3.5


def change_file_ext(path: str, ext: str = None) -> str:
    fn, _ = os.path.splitext(path)
    if ext is None:
        return fn
    return f"{fn}.{ext}"


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='whisper_client',
        description='Transcribe an audio file'
    )
    parser.add_argument(
        '--language', '-l',
        help="Define the audio language",
        default=None, required=False
    )
    parser.add_argument('--output', '-o', help='Ouput path', default=None, required=False)
    parser.add_argument('filename')

    args: argparse.Namespace = parser.parse_args()
    input_fn: str = args.filename

    options: dict[str, typing.Any] = {
        'language': args.language,
        'file_size': os.path.getsize(input_fn)
    }

    with Socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.settimeout(TIMEOUT)
        conn.connect((config.HOSTNAME, config.SERVER_PORT))
        conn.settimeout(None)
        ut.read_reliably(conn, config.BUFFER_SIZE)

        options_as_bytes: bytes = pickle.dumps(options)
        #options_size: int = len(options_as_bytes)
        #ut.write_reliably(conn, options_size.to_bytes(config.INT_SIZE), config.INT_SIZE)
        #time.sleep(3)
        ut.write_reliably(conn, options_as_bytes, config.BUFFER_SIZE)

        written_bytes: int = 0
        with open(input_fn, 'rb') as fh:
            while True:
                chunk: bytes = fh.read(config.BUFFER_SIZE)
                if chunk is None or len(chunk) == 0:
                    break
                written_bytes += ut.write_reliably(conn, chunk, config.BUFFER_SIZE)

        print(f'done (wrote {written_bytes} bytes)')

        result_size: int = int.from_bytes(ut.read_reliably(conn, config.INT_SIZE))
        result: bytes = ut.from_bytes(ut.read_reliably(conn, result_size))
        print(f"transcribed text has size {result_size}")

        output_fn: str = args.output
        output_fn = output_fn if output_fn is not None else change_file_ext(input_fn, 'txt')
        with open(output_fn, 'w') as fh:
            fh.write(result)
            fh.flush()


if __name__ == '__main__':
    main()
