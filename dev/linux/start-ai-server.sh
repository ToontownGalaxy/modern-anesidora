#!/bin/sh
cd ../../

# Define some constants for our AI server:
MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="127.0.0.1:7100"
EVENTLOGGER_IP="127.0.0.1:7198"
DISTRICT_NAME="Gravity Falls"

# Get the user input:
read -p "Base channel (DEFAULT: 401000000): " BASE_CHANNEL
BASE_CHANNEL=${BASE_CHANNEL:-401000000}

echo "==============================="
echo "Starting Disney's Toontown Online AI server..."
echo "District name: $DISTRICT_NAME"
echo "Base channel: $BASE_CHANNEL"
echo "Max channels: $MAX_CHANNELS"
echo "State Server: $STATESERVER"
echo "Astron IP: $ASTRON_IP"
echo "Event Logger IP: $EVENTLOGGER_IP"
echo "==============================="

while [ true ]
do
    /usr/bin/python3 -m toontown.ai.AIStart
done
