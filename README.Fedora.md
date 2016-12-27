Notes on Fedora bup Package
===========================

Changes requiring attention when upgrading from 0.27 to 0.28.1
--------------------------------------------------------------

- The index format has changed, which will trigger a full index rebuild on the
  next index run, making that run more expensive than usual.

- When given `--xdev`, `bup save` should no longer skip directories that are
  explicitly listed on the command line when the directory is both on a
  separate filesystem, and a subtree of another path listed on the command
  line.  Previously `bup save --xdev / /usr` could skip "/usr" if it was on a
  separate filesystem from "/".

- Tags along a branch are no longer shown in the branch's directory in
  the virtual filesystem (VFS).  For example, given `bup tag special
  /foo/latest`, "/foo/special" will no longer be visible via `bup ls`,
  `bup web`, `bup fuse`, etc., but the tag will still be available as
  "/.tag/special".

- In version 0.27 (and previous versions), a `--sparse` restore might have
  produced incorrect data.  Please treat any existing `--sparse` restores as
  suspect.  The problem should be fixed in version 0.27.1.

For the complete list of changes and bug fixes, consult:
- %{_pkgdocdir}/0.28.1-from-0.28.md,
- %{_pkgdocdir}/0.28-from-0.27.1.md,
- %{_pkgdocdir}/0.27.1-from-0.27.md.

The `par2` support in `bup fsck` is enabled in versions >= 0.28.1
-----------------------------------------------------------------

Support for generating and/or using "recovery blocks" with the external `par2`
tool in `bup fsck` command is enabled again since the new version of
par2cmdline package (>= 0.6.14) provides a working version of `par2` tool.


Authors
-------

Tadej Janež
