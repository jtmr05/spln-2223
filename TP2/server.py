#!/usr/bin/env python3

import whisper
import threading
import socket
import pickle

MODEL: str = 'small'
PORT: int = 9000
BUFFER_SIZE: int = 4096


def as_bytes(s: str) -> bytes:
    return s.encode('utf-8')


def from_bytes(b: bytes) -> str:
    return b.decode('utf-8')


class WhisperServer:

    _model: whisper.Whisper
    _queue: list[dict]
    _queue_lock: threading.Condition
    _requests_socket: socket.socket
    _responses_socket: socket.socket

    def __init__(self):
        self._model = whisper.load_model(MODEL)
        self._queue = list()
        self._queue_lock = threading.Condition()
        self._requests_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._requests_socket.bind(('', PORT))
        self._responses_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._requests_socket.close()
            self._responses_socket.close()
        finally:
            pass

    def _listen(self):

        print(f"Server listening on port {PORT}")

        while True:
            (content, address) = self._requests_socket.recvfrom(BUFFER_SIZE)
            content = pickle.loads(content)

            try:
                self._queue_lock.acquire()
                self._queue.append((content, address))
                self._queue_lock.notify_all()
            finally:
                self._queue_lock.release()

    def _handle_requests(self):
        while True:
            try:
                self._queue_lock.acquire()
                while len(self._queue) == 0:
                    self._queue_lock.wait()
                content, address = self._queue.pop(0)
            finally:
                self._queue_lock.release()

            audio = whisper.load_audio(content['filename'])
            audio = whisper.pad_or_trim(audio)

            mel = whisper.log_mel_spectrogram(audio).to(self._model.device)
            options = whisper.DecodingOptions(
                task=content.get('task', 'transcribe'),  # TODO add some more??
                language=content.get('lang', None)
            )
            result = whisper.decode(self._model, mel, options)
            print(result.text)

            self._responses_socket.sendto(pickle.dumps(len(result.text)), address)
            self._responses_socket.sendto(as_bytes(result.text), address)

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
