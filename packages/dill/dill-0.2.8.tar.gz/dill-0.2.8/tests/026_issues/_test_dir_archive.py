'''
If, for example, dir_archive is used with flattened keys the str() encoding of those tuples yields directory names with parenthesis, and these ultimately do not correctly load if the archive is written non-pickled (i.e., as python objects) because invalid characters are used in the import statement that is exec()ed. There also seem to be some hacks relative to reloading the archive from disk, in particular

_getkey contains [2:] vs being based on the value of PREFIX
the interactions between _getdir _getkey and _lookup make various assumptions which I believe frustrate causing _fname to meaningfully modify the text representation of keys as "good" filenames
_lookup in particular does not distinguish between calls made to it where the key parameter is coming from a directory name vs really being a key (sequence is _keydict()-->_getkey()-->_lookup()-->_getdir() ), implying the assumed equivalence of dir and key encodings.
I've fixed some problems in a branch, e.g., by adding a parameter to _lookup(...,isdir=False) allowing me to implement a filename encoding in _fname which eliminates problematic characters. This yields the ability to have relatively clear-text directory names, and python object storage that works. I.e., a disk cache that is easily understood by human eyes. This makes the cache useful as a backing store for, for example, function values used to replay behavior in testing frameworks. E.g., run the program once with nothing in the dir_archive, then run it again from a full dir_archive to regression test the parts that rely on the functions that got cached.

I can submit a pull request, but see 0 pull requests here, so I'm wondering if you're accepting community input here.

... I'm also wondering why _hasinput() doesn't use os.path.isfile().
'''
