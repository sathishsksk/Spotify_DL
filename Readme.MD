# Music downloader bot

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

![Logo](https://camo.githubusercontent.com/9e110f81b4ebd98bf8efaf1a202a472ea7fbb49634265c1912b4515e731a207b/68747470733a2f2f74656c656772612e70682f66696c652f6637653166333038653336346266366132373434392e6a7067)

Still under development Please Report issues to improve this repo.I will try to fix bugs in next update

Music downloader bot is a telegram bot that can send you high-quality audio 🎧🎧🎧

## Features

- All jio saavn Song,Album and Playlist links are supported
- Meta data such as Album Art, artist details are present
- Lyrics are also embeded into the meta data (if available)

## Deployment

### Please read all the deployment instructions before deploying the bot

This project entirely depends on [Sumanjay's](https://github.com/cyberboysumanjay)
[Unofficial jiosaavn api](https://github.com/cyberboysumanjay/JioSaavnAPI).

So if You need to deply this project you first have to deply your own JioSaavnAPI

how to install:-
 
 1.edit the BOT_TOKEN in bot.py
 2.edit the API in helpers/downloader.py
 3.then deploy the bot
 
deploy in docker
 
 1.git clone git 'repo'
 2.cd 'repo name'
 3.docker login
 4.docker build . -t 'repo'
 5.docker tag 'repo' 'dockerusername'/'repo'
 6.docker push 'dockerusername'/'repo'
 7.docker run -p 8080 'dockerusername'/'repo'
 
 your bot deployed in your vps
