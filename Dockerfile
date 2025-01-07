FROM python:3.10.4-slim-buster

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN apt -qq update && apt -qq install -y git wget pv jq python3-dev mediainfo gcc aria2 libsm6 libxext6 libfontconfig1 libxrender1 libgl1-mesa-glx ffmpeg

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["bash","run.sh"]
