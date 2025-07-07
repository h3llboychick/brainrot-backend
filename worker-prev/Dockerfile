FROM python:3.12.6-alpine

WORKDIR /worker

COPY requirements.txt main.py __init__.py setup.py /worker

RUN mkdir -p video_formats common

COPY video_formats video_formats
COPY common common

RUN apk add gcc musl-dev linux-headers python3-dev
RUN apk add libffi-dev
RUN apk add imagemagick freetype-dev ttf-dejavu
RUN apk add --no-cache ffmpeg
COPY Proxima-Nova-Bold.otf /usr/share/fonts/

# Run fc-cache to update font cache
RUN fc-cache -f -v

RUN fc-list | grep "Proxima"


RUN pip3 install -r requirements.txt
RUN pip3 install -e .

RUN cd /worker
CMD ["python3", "./main.py"]