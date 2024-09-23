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
# Usage
You can use both - website (only for registration and more easy passage to telegram) or telegram only.
## Website
#### You can register you account and after registration there will be a link to go to telegram (this way you can scip the registration and immediately start to use you account)
##### The layout to this is in backend/templates/register.html
## Telegram only
#### You can register you account directly in telegram and after that start to use your account 
## Notifications 
#### It doesn't matter which way did you choose, If the registration and binding completed successfully you will see four buttons - to get notification, update notification, delete notification and create notification
