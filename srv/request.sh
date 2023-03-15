#!/bin/sh
curl 127.0.0.1:8008 -H "Content-Type: application/json" --request POST -d @request_data.json | jq

