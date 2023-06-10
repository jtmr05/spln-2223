#!/usr/bin/env python3

import numpy as np
import pickle
import socket
import threading
import typing
import whisper

import utils as ut
from config import *

Socket = socket.socket
Address = tuple[str, int]  # a hostname/port pair

FILE_PATH: str = '/tmp/whisper_server.tmp'
TIMEOUT: float = 3.0


class WhisperServer:

    _model: whisper.Whisper
    _queue: list[tuple[Socket, Address]]
    _queue_lock: threading.Condition
    _socket: Socket

    def __init__(self):
        self._model = whisper.load_model(MODEL)
        self._queue = list()
        self._queue_lock = threading.Condition()
        self._socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((HOSTNAME, SERVER_PORT))
        self._socket.listen()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self._socket.close()
        finally:
            pass

    def _listen(self):

        prefix: str = ut.annotate('::', 1, 34)

        print(f"{prefix} server listening for requests on port {ut.annotate(SERVER_PORT, 1)}...")
        while True:
            pair: tuple[Socket, Address] = self._socket.accept()
            addr_as_str: str = ut.annotate(f"{pair[1][0]}:{pair[1][1]}", 1)

            print(f"{prefix} received new request from {addr_as_str}")

            with self._queue_lock:
                self._queue.append(pair)
                self._queue_lock.notify_all()

    def _handle_requests(self):

        prefix: str = ut.annotate('==>', 1, 32)

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
            ut.write_reliably(conn, bytes(BUFFER_SIZE), BUFFER_SIZE)

            print(f"{prefix} reading options from the client now")

            # read the options from the client (file size, language, ...)
            #options_size_as_bytes: bytes = ut.read_reliably(conn, INT_SIZE)
            #options_size: int = int.from_bytes(options_size_as_bytes)
            #print(f"{prefix} options_size == {options_size}")
            options_as_bytes: bytes = ut.read_reliably(conn, BUFFER_SIZE)
            options: dict[str, typing.Any] = pickle.loads(options_as_bytes)
            print(f"{prefix} options: {ut.annotate(options, 1)}")
            file_size: int = options.pop('file_size')

            conn.settimeout(TIMEOUT)

            try:
                audio_content: bytes = ut.read_reliably(conn, file_size, True)
                print(len(audio_content))
                with open(FILE_PATH, 'wb') as fh:
                    fh.write(audio_content)
                    fh.flush()

                print(f"{prefix} file successfully received")

                audio: np.ndarray = whisper.load_audio(FILE_PATH)
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

            finally:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

    def run(self):
        t1 = threading.Thread(target=self._listen)
        t2 = threading.Thread(target=self._handle_requests)

        t1.start(); t2.start()
        t1.join(); t2.join()


def main():
    with WhisperServer() as ws:
        ws.run()


if __name__ == '__main__':
    main()
