FROM selenium/video:ffmpeg-4.3.1-20230404

USER root

RUN dpkg --configure dbus && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --fix-missing && \
    apt-get install -y ffmpeg

USER seluser