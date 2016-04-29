ZOCP Inotify Actor
==================

This is a Actor which watches a directory. Simple provide the directory name and it will signal the filesystem events in that
directory.

Note:

* this code is a proof of concept and will only watch DELETE events
* it only works on linux. It can be ported to OSX, I guess. Windows ... yeah whatever.
