FROM python:3

ENV WHISPER_MODEL=small
ENV WHISPER_HOSTNAME=localhost
ENV WHISPER_PORT=8888

WORKDIR /server

RUN apt update 
RUN apt upgrade -y
RUN apt install ffmpeg -y

RUN pip install --upgrade pip
RUN pip install openai-whisper 
RUN pip install noisereduce

COPY server.py ./
COPY utils.py ./

RUN chmod +x server.py

EXPOSE 8888

CMD ./server.py $WHISPER_MODEL $WHISPER_HOSTNAME $WHISPER_PORT
