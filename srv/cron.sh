#!/bin/sh

PATH=/usr/local/bin:$PATH
cd /home/simon/Cosillas/entrees/pyentrees/srv

/home/simon/.local/bin/pipenv run python src/server.py >> logs_cron 2>&1
