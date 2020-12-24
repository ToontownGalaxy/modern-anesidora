cd "$(dirname "$0")"
cd ../..
cd ..
export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
read -p "Username: " ttgUsername
read -p "Gameserver (DEFAULT:  45.55.208.151): " TTG_GAMESERVER
TTG_GAMESERVER=${TTG_GAMESERVER:-"45.55.208.151"}

# Export the environment variables:
export ttgUsername=$ttgUsername
export ttgPassword="password"
export TTG_PLAYCOOKIE=$ttgUsername
export TTG_GAMESERVER=$TTE_GAMESERVER

echo "==============================="
echo "Starting Disney's Toontown Online..."
echo "Username: $ttgUsername"
echo "Gameserver: $TTG_GAMESERVER"
echo "==============================="

ppython -m toontown.toonbase.ToontownStart
