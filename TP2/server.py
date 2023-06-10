#!/usr/bin/env python3

import numba.core.errors as numba_errs
import warnings

if True:
    warnings.simplefilter('ignore', category=numba_errs.NumbaDeprecationWarning)
    warnings.simplefilter('ignore', category=numba_errs.NumbaPendingDeprecationWarning)

import argparse
import noisereduce as nr
import numpy as np
import pickle
import socket
import threading
import typing
import whisper

import utils as ut

Address = tuple[str, int]  # a hostname/port pair
ArgParser = argparse.ArgumentParser
Socket = socket.socket
Thread = threading.Thread

BUFFER_SIZE: int = 2048
FILE_PATH: str = '/tmp/whisper_server.tmp'
INT_SIZE: int = 64
TIMEOUT: float = 3.5


class WhisperServer:

    _model: whisper.Whisper
    _queue: list[tuple[Socket, Address]]
    _queue_lock: threading.Condition
    _socket: Socket
    _port: int

    def __init__(self, model_name: str, hostname: str, port: int):
        self._model = whisper.load_model(model_name)
        self._queue = list()
        self._queue_lock = threading.Condition()
        self._socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((hostname, port))
        self._socket.listen()
        self._port = port

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self._socket.close()
        finally:
            pass

    def _listen(self):

        prefix: str = ut.annotate('::', 1, 34)

        print(f"{prefix} server listening for requests on port {ut.annotate(self._port, 1)}...")
        while True:
            pair: tuple[Socket, Address] = self._socket.accept()
            addr_as_str: str = ut.annotate(f"{pair[1][0]}:{pair[1][1]}", 1)

            print(f"{prefix} received new request from {addr_as_str}")

            with self._queue_lock:
                info_str: str = f"there are {len(self._queue)} requests in queue"
                info_str_as_bytes: bytes = ut.as_bytes(info_str)
                info_str_len: int = len(info_str)
                ut.write_reliably(pair[0], info_str_len.to_bytes(INT_SIZE), INT_SIZE)
                ut.write_reliably(pair[0], info_str_as_bytes, info_str_len)
                self._queue.append(pair)
                self._queue_lock.notify_all()

    def _handle_requests(self):

        prefix: str = ut.annotate('==>', 1, 32)
        skip_shutdown: bool = False

        while True:
            with self._queue_lock:
                while len(self._queue) == 0:
                    print(f"{prefix} waiting for new requests...")
                    self._queue_lock.wait()

                pair: tuple[Socket, Address] = self._queue.pop(0)
                conn, addr = pair
                addr_as_str: str = ut.annotate(f"{addr[0]}:{addr[1]}", 1)

            print(f"{prefix} handling request for client {addr_as_str}")

            # ping client, informing that it's their turn
            ut.write_reliably(conn, bytes(1), 1)

            conn.settimeout(TIMEOUT)

            try:
                # read the options from the client (file size, language, ...)
                print(f"{prefix} reading options from the client")
                options_size: int = int.from_bytes(ut.read_reliably(conn, INT_SIZE))
                options_as_bytes: bytes = ut.read_reliably(conn, options_size)
                options: dict[str, typing.Any] = pickle.loads(options_as_bytes)

                print(f"{prefix} options: {ut.annotate(options, 1)}")

                file_size: int = options.pop('file_size')
                noise_reduction: bool = options.pop('noise_reduction')
                sample_rate: int = options.pop('sample_rate')
                if sample_rate is None:
                    sample_rate = whisper.audio.SAMPLE_RATE

                audio_content: bytes = ut.read_reliably(conn, file_size)
                with open(FILE_PATH, 'wb') as fh:
                    fh.write(audio_content)
                    fh.flush()

                print(f"{prefix} file successfully received")

                audio: np.ndarray = whisper.load_audio(FILE_PATH, sample_rate)
                if noise_reduction:
                    print(f"{prefix} performing noise reduction")
                    audio = nr.reduce_noise(y=audio, sr=sample_rate)

                result: dict[str, typing.Any] = whisper.transcribe(self._model, audio, **options)

                print(f"{prefix} finished transcription; sending result to client")
                result_as_bytes: bytes = ut.as_bytes(result['text'])
                result_size: int = len(result_as_bytes)
                ut.write_reliably(conn, result_size.to_bytes(INT_SIZE), INT_SIZE)
                ut.write_reliably(conn, result_as_bytes, result_size)

                print(f"{prefix} finalizing request for {addr_as_str}...")

            except TimeoutError:
                print(f"{prefix} connection timed out; continuing...")
                continue

            except BrokenPipeError:
                print(f"{prefix} connection to client lost; continuing...")
                skip_shutdown = True
                continue

            finally:
                if not skip_shutdown:
                    conn.shutdown(socket.SHUT_RDWR)
                skip_shutdown = False
                conn.close()

    def run(self):
        try:
            t1: Thread = Thread(target=self._listen)
            t2: Thread = Thread(target=self._handle_requests)

            t1.daemon = True; t2.daemon = True
            t1.start(); t2.start()
            t1.join(); t2.join()

        except KeyboardInterrupt:
            print(f"\n{ut.annotate('@@', 1, 31)} server shutting down...")


def main():
    parser: ArgParser = ArgParser(
        prog='whisper-server',
        description='Whisper audio transcription server'
    )
    parser.add_argument('model', help="HuggingFace model to be used")
    parser.add_argument('hostname')
    parser.add_argument('port', type=int)

    args: argparse.Namespace = parser.parse_args()

    with WhisperServer(args.model, args.hostname, args.port) as ws:
        ws.run()


if __name__ == '__main__':
    main()
