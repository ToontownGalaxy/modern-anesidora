cd "$(dirname "$0")"
cd ../../../
export MAX_CHANNELS=999999
export STATESERVER=4002
export ASTRON_IP=127.0.0.1:7100
export EVENTLOGGER_IP=127.0.0.1:7198
export BASE_CHANNEL=1000000
export PYTHONPATH=dependencies/mac/lib:$PYTHONPATH
ppython -m toontown.uberdog.UDStart 