MAJOR = 0
MINOR = 2
MICRO = 2
LEVEL = 'release'
SERIAL = 0

RELEASE = '.'.join([str(x) for x in (MAJOR, MINOR, MICRO)])
VERSION = '.'.join([str(x) for x in (MAJOR, MINOR)])
version_info = (MAJOR, MINOR, MICRO, LEVEL, SERIAL)
