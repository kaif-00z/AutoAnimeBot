FROM python:3.10.4-slim-buster
RUN mkdir /bot && chmod 777 /bot
WORKDIR /bot
ENV DEBIAN_FRONTEND=noninteractive
RUN apt -y update && add-apt-repository -y ppa:qbittorrent-team/qbittorrent-stable
RUN apt -qq update && apt -qq install -y git wget pv jq python3-dev qbittorrent-nox ffmpeg mediainfo gcc
COPY . .
RUN pip3 install -U -r requirements.txt
CMD ["bash","run.sh"]
