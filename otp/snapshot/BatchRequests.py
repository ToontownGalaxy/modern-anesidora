import sys
import time
import urllib.request, urllib.parse, urllib.error
import string

if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("usage: cat avIDs.txt | BatchRequests.py HOSTNAME PORTNUMBER")
    sys.exit(1)
assert len(sys.argv) == 3

hostname = sys.argv[1]
portnum = int(sys.argv[2])

ids = sys.stdin.readlines()

ids = list(map(string.strip,ids))

opener = urllib.request.FancyURLopener({})

for avId in ids:
    print(("%s..." % avId), end=' ')
    f = opener.open("http://%s:%s/queueSnapshot?avatarId=%s" % (hostname,portnum,avId))
    #f.read()  # Do this if we want to check the result...which we don't if we want to be fast
    print("done")
