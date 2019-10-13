FROM python:3.4.7-stretch

WORKDIR /usr/src/app

RUN git clone https://github.com/kandnub/TG-UserBot.git /usr/src/app

COPY ./config.ini ./userbot.session* /usr/src/app/TG-UserBot/

WORKDIR usr/src/app/TG-UserBot/

RUN pip3 install --user --no-cache-dir -r requirements.txt

# CMD ["echo", "done"]
CMD ["redis-server", "&", "&&", "python3", "-m", "userbot"]
