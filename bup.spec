# Uncomment the following RPM macro if you use a prerelease version:
# %%global prerelease rc4
%global commit d612d9a599590cb53a76711754f9e031f66a330a

Name: bup
Version: 0.27
Release: 0.1%{?prerelease:.%{prerelease}}%{?dist}
Summary: Very efficient backup system based on the git packfile format

# all of the code is licensed as GNU Lesser General Public License v2, except:
# - lib/bup/bupsplit.c: BSD License (two clause),
# - lib/bup/bupsplit.h: BSD License (two clause),
# - lib/bup/options.py: BSD License (two clause),
# - definition of relpath() function in wvtest.py: Python License
License: LGPLv2 and BSD and Python
URL: https://bup.github.io/
Source0: https://github.com/%{name}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1: README.Fedora

# Replace calls to 'python' with calls to '$PYTHON' in all tests. In
# combination with setting the 'PYTHON' environment variable to 'python2', this
# ensures compatibily after switching to Python3 by default.
Patch0: 0001-Tests-replace-calls-to-python-with-calls-to-PYTHON.patch
# Replace all python shebangs with explicit python2 shebangs. This will ensure
# compatibility after switching to Python3 by default.
Patch1: 0002-Replace-all-python-shebangs-with-explicit-python2-sh.patch
# Update GNU LGPLv2 license text with the latest version.
Patch2: 0003-LICENSE-update-to-the-current-GNU-LGPLv2-text.patch
# Prevent building and installation of bup's HTML documentation since it
# doesn't add any value (it is the same as man pages).
Patch3: 0004-Prevent-building-and-installation-of-HTML-documentat.patch
# Remove support for 'par2' due to issues with the version in Fedora
# For more info, see README.Fedora
Patch4: 0005-Remove-support-for-par2-due-to-issues-with-the-versi.patch

BuildRequires: python2-devel
BuildRequires: git
# Required for building documentation
BuildRequires: pandoc

Requires: git
Requires: pyxattr
Requires: pylibacl
# Only required for 'bup fuse' command
Requires: fuse-python
# Only required for 'bup web' command
Requires: python-tornado


%description
Very efficient backup system based on the git packfile format, providing fast
incremental saves and global deduplication (among and within files, including
virtual machine images). Some of its features are:
* It uses a rolling checksum algorithm and hence it can backup huge files
  incrementally.
* It uses packfile format from git, so one can access the stored data even if
  he doesn't like bup's user interface.
* It writes packfiles directly so it is fast even with huge amounts of data:
  it can track millions of files and keep track of hundreds or thousands of
  gigabytes of objects.
* Data is "automagically" shared between incremental backups without having to
  know which backup is based on which other one.
* One can make a backup directly to a remote bup server, without needing tons
  of temporary disk space on the computer being backed up. If the backup is
  interrupted halfway through, the next run will pick up where the previous
  backup left off.
* It can use "par2" redundancy to recover corrupted backups even if the disk
  has undetected bad sectors.
* Each incremental backup acts as if it's a full backup, it just takes less
  disk space.
* One can mount a bup repository as a FUSE filesystem and access the contents
  that way, or even export it over Samba.


%prep
%autosetup -n %{name}-%{commit} -S git
cp %{SOURCE1} .


%build
# NOTE: bup uses a non-standard configure script which is executed during the
# execution of the make command.
# To configure the build process, we need to pass variables to the make
# command.
make %{?_smp_mflags} CFLAGS="${CFLAGS:-%optflags}" PYTHON=%{__python2}


%install
# NOTE: bup uses a non-standard configure script, which doesn't support
# specifying distro-specific paths of the variables defined below.
# To set the paths, we need to manually pass variables to the make command.
make install MANDIR=%{buildroot}%{_mandir} \
    DOCDIR=%{buildroot}%{_docdir}/{%name} BINDIR=%{buildroot}%{_bindir} \
    LIBDIR=%{buildroot}%{_libdir}/%{name} PYTHON=%{__python2}

# Fix hard-coded libdir location in bup's executable
sed -i 's|/lib/bup|/%{_lib}/bup|' %{buildroot}%{_bindir}/bup


%check
# Run the built-in test suite containing 3800+ tests
# (it takes < 100 seconds on a modern computer)
make test PYTHON=%{__python2}


%files
%doc README.md README.Fedora
%license LICENSE
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*


%changelog
* Sun May 17 2015 Tadej Janež <tadej.j@nez.si> 0.27-0.1
- Initial package.
