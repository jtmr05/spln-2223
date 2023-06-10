FROM python:3

ENV WHISPER_MODEL=small
ENV WHISPER_HOSTNAME=localhost
ENV WHISPER_PORT=8888

WORKDIR /server

# COPY requirements.txt ./

# RUN pip install -r requirements.txt

RUN pip install openai-whisper noisereduce

COPY server.py ./
COPY utils.py ./

RUN chmod +x server.py

EXPOSE 8888

CMD [ "./server.py", "$WHISPER_MODEL",, "$WHISPER_HOSTNAME", "$WHISPER_PORT" ]
