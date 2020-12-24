cd "$(dirname "$0")"
cd ..
cd ..
cd ..
export PYTHONPATH=dependencies/mac/lib:$PYTHONPATH
export DYLD_FRAMEWORK_PATH="Frameworks"
# Get the user input:
read -p "Username: " ttgUsername

# Export the environment variables:
export ttgUsername=$ttgUsername
export ttgPassword="password"
export TTG_PLAYCOOKIE=$ttgUsername
export TTG_GAMESERVER="127.0.0.1"

echo "==============================="
echo "Starting Disney's Toontown Online..."
echo "Username: $ttgUsername"
echo "Gameserver: $TTG_GAMESERVER"
echo "==============================="

ppython -m toontown.toonbase.ToontownStart
