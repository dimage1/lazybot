# syntax=docker/dockerfile:1

# base python image for custom image
FROM python:3.9.13-slim-buster

# create working directory and install pip dependencies
WORKDIR /lazybot
RUN pip install requests prettytable python-dotenv
RUN pip install pyTelegramBotAPI 
RUN pip install timezonefinderL

# copy python project files from local to /lazybot image working directory
COPY bot.py .
ADD utils ./utils/
ADD blabla ./blabla/

# run server  
CMD [ "python3", "bot.py"]

