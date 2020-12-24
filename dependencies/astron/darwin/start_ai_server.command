cd "$(dirname "$0")"
cd ../../../

export MAX_CHANNELS=999999
export STATESERVER=4002
export ASTRON_IP=127.0.0.1:7100
export EVENTLOGGER_IP=127.0.0.1:7198

export DISTRICT_NAME="Nutty River"
export BASE_CHANNEL=401000000

echo ===============================
echo Starting Disney's Toontown Online AI server...
echo ppython: "ppython"
echo District name: $DISTRICT_NAME
echo Base channel: $BASE_CHANNEL
echo Max channels: $MAX_CHANNELS
echo State Server: $STATESERVER
echo Astron IP: $ASTRON_IP
echo Event Logger IP: $EVENTLOGGER_IP
echo ===============================
export PYTHONPATH=dependencies/mac/lib:$PYTHONPATH
ppython -m toontown.ai.AIStart 
