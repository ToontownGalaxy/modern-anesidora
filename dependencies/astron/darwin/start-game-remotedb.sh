#!/bin/sh
cd ..
cd ..
export PYTHONPATH=dependencies/mac/lib:$PYTHONPATH
export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
read -p "Username: " tteUsername
read -s -p "Password: " ttePassword
echo
read -p "Gameserver (DEFAULT: 167.114.28.238): " tte_GAMESERVER
tte_GAMESERVER=${TTE_GAMESERVER:-"167.114.28.238"}

# Export the environment variables:
export tteUsername=$tteUsername
export ttePassword=$ttePassword
export tte_PLAYCOOKIE=$tteUsername
export tte_GAMESERVER=$tte_GAMESERVER

echo "==============================="
echo "Starting Disney's Toontown Online..."
echo "Username: $tteUsername"
echo "Gameserver: $TTE_GAMESERVER"
echo "==============================="

ppython -m toontown.toonbase.ToontownStartRemoteDB
