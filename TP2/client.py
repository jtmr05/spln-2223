#!/usr/bin/env python3

import argparse
import os
import pickle
import socket
import sys

import utils as ut

ArgParser = argparse.ArgumentParser
Socket = socket.socket

BUFFER_SIZE: int = 2048
INT_SIZE: int = 64
TIMEOUT: float = 3.5


def change_file_ext(path: str, ext: str = None) -> str:
    fn, _ = os.path.splitext(path)
    if ext is None:
        return fn
    return f"{fn}.{ext}"


def main():
    parser: ArgParser = ArgParser(prog='whisper-client', description='Transcribe an audio file')
    parser.add_argument(
        '--language', '-l',
        help="Define the audio language",
        default=None, required=False
    )
    parser.add_argument(
        '--noise-reduction', '-n',
        help="Perform a noise reduction on the audio file before transcribing",
        action=argparse.BooleanOptionalAction,
        default=False
    )
    parser.add_argument(
        '--sample-rate', '-s',
        default=None, required=False,
        type=int
    )
    parser.add_argument('--output', '-o', help='Ouput path', default=None, required=False)
    parser.add_argument('filename')
    parser.add_argument('hostname', help='The hostname of the Whisper server instance')
    parser.add_argument('port', type=int, help='The port on which the server is listening')

    args: argparse.Namespace = parser.parse_args()
    input_fn: str = args.filename

    options: dict[str, typing.Any] = {
        'language': args.language,
        'file_size': os.path.getsize(input_fn),
        'noise_reduction': args.noise_reduction,
        'sample_rate': args.sample_rate
    }

    conn: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.settimeout(TIMEOUT)
        conn.connect((args.hostname, args.port))
        conn.settimeout(None)

        info_str_size: int = int.from_bytes(ut.read_reliably(conn, INT_SIZE))
        info_str: str = ut.from_bytes(ut.read_reliably(conn, info_str_size))
        print(f"Server message: {ut.annotate(info_str, 2)}")

        ut.read_reliably(conn, 1)

        options_as_bytes: bytes = pickle.dumps(options)
        options_size: int = len(options_as_bytes)
        ut.write_reliably(conn, options_size.to_bytes(INT_SIZE), INT_SIZE)
        ut.write_reliably(conn, options_as_bytes, options_size)

        with open(input_fn, 'rb') as fh:
            while True:
                chunk: bytes = fh.read(BUFFER_SIZE)
                if chunk is None or len(chunk) == 0:
                    break
                ut.write_reliably(conn, chunk, len(chunk))

        result_size: int = int.from_bytes(ut.read_reliably(conn, INT_SIZE))
        result: bytes = ut.from_bytes(ut.read_reliably(conn, result_size))

        output_fn: str = args.output
        output_fn = output_fn if output_fn is not None else change_file_ext(input_fn, 'txt')

        os.makedirs(os.path.dirname(output_fn), exist_ok=True)

        with open(output_fn, 'w') as fh:
            fh.write(result)
            fh.flush()

    except KeyboardInterrupt:
        print("\nCanceling request...", file=sys.stderr)

    finally:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


if __name__ == '__main__':
    main()
