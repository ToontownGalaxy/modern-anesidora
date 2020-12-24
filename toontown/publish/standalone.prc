# This prc file is provided by default in the
# panda-standalone.zip file generated by make-panda-standalone.sh.

# Maya might use up a lot of display memory, and then DX8 can't open a
# window and panic exits, taking Maya down with it.  GL seems to be able
# to open a window, though.
#load-display pandadx8
load-display pandagl

# Push the far plane back enough not to be a nuisance.
default-far 2000

# And the near plane forward enough to reduce Z-fighting.
default-near 0.5

# Let's try enabling the model cache.
model-cache-dir /c/temp/panda-cache
model-cache-max-kbytes 102485760

# Let's have the artists filter the appearance through the $PMODELS
# textures.txa file for now.  We point them at the file checked out on
# the build server.
texture-filter txafile
txa-file /hosts/new-dragon/build/install/pmodels/src/maps/textures.txa