#!/bin/sh
cd ../../..

# Define some constants for our AI server:
MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="158.69.28.83:7100"
EVENTLOGGER_IP="158.69.28.83:7198"

# Get the user input:
read -p "District name (DEFAULT: Gravity Falls): " DISTRICT_NAME
DISTRICT_NAME=${DISTRICT_NAME:-Gravity Falls}
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
    python -m toontown.ai.ServiceStart --base-channel $BASE_CHANNEL \
                     --max-channels $MAX_CHANNELS --stateserver $STATESERVER \
                     --astron-ip $ASTRON_IP --eventlogger-ip $EVENTLOGGER_IP \
                     --district-name $DISTRICT_NAME
done
