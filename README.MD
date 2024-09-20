# Project Setup

This document outlines the steps to set up the project using Docker Compose. The project consists of three main services: Redis, Backend, and Telegram Bot.

## Environment Variables

Before starting the services, ensure that you have replaced an <bot_token> in .env in the root directory file to real token.


Replace your_bot_token_here with your actual Telegram Bot token.

## Setting Up the Project

To set up the project, ensure that you have installed docker and docker-compose on your device
and gave them such privileges (or run using sudo, for example) and run this command:
```shell script
docker compose up -d --build
```



