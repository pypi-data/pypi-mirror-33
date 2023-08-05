#BufferedRandomType = type(open(os.devnull, 'r+b', buffering=-1))
#BufferedReaderType = type(open(os.devnull, 'rb', buffering=-1))

# we open /dev/null, and then discard the file handle without closing it first.

import subprocess as sb

BufferedReaderType = type(getattr(sb, 'DEVNULL', open(os.devnull, 'rb', buffering=-1)))
