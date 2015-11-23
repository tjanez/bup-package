Notes on Fedora bup Package
===========================


The `par2` support in `bup fsck` is disabled
--------------------------------------------

Support for generating and/or using "recovery blocks" with the external `par2`
tool in `bup fsck` command is intentionally disabled since the current packaged
version of `par2` (part of the par2cmdline package) is outdated and can leave
files in worse condition than before running `par2`.
A bug report asking about the future of par2cmdline tool has been filed in
Red Hat Bugzilla: https://bugzilla.redhat.com/show_bug.cgi?id=1221165.


Authors
-------

Tadej Janež
