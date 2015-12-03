# Uncomment the following RPM macro if you use a prerelease version:
# %%global prerelease rc4
%global commit d612d9a599590cb53a76711754f9e031f66a330a

Name: bup
Version: 0.27
Release: 0.4%{?prerelease:.%{prerelease}}%{?dist}
Summary: Very efficient backup system based on the git packfile format

# all of the code is licensed as GNU Lesser General Public License v2, except:
# - lib/bup/bupsplit.c: BSD License (two clause),
# - lib/bup/bupsplit.h: BSD License (two clause),
# - lib/bup/options.py: BSD License (two clause),
# - definition of relpath() function in wvtest.py: Python License
License: LGPLv2 and BSD and Python
URL: https://bup.github.io/
Source0: https://github.com/%{name}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1: README.Fedora.md
Source2: bup-web.service
Source3: README-bup-web.Fedora.md

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
# Temporarily disable test_from_path_error() test that fails on Fedora Koji
# and COPR build systems.
# This issue has been reported upstream:
# https://groups.google.com/d/msg/bup-list/7K0gD274i_A/6ZjA1La6VK8J
Patch5: 0006-Disable-test_from_path_error-test-that-fails-on-Fedo.patch

BuildRequires: python2-devel
BuildRequires: git
# Required for building documentation
BuildRequires: pandoc
# Required for preparing systemd service for 'bup web' command
BuildRequires: systemd
# Required for running tests
BuildRequires: perl(Time::HiRes)

Requires: git
Requires: pyxattr
Requires: pylibacl
# Only required for 'bup fuse' command
Requires: fuse-python


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

#
# bup-web
#
%package web
License: LGPLv2
Summary: Web server for browsing through bup repositories
URL: https://bup.github.io/
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: python-tornado
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description web
Provides the "bup web" command which runs a web server for browsing through
bup repositories.


%prep
%autosetup -n %{name}-%{commit} -S git
cp %{SOURCE1} .
mkdir bup-web
cp %{SOURCE3} bup-web/README.Fedora.md


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

# Install systemd unit file
mkdir -p %{buildroot}%{_userunitdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_userunitdir}

%check
# Run the built-in test suite containing 3800+ tests
# (it takes < 100 seconds on a modern computer)
make test PYTHON=%{__python2}


%post web
# NOTE: %%systemd_user_post macro is currently broken.
# Upstream pull request: https://github.com/systemd/systemd/pull/1986
# After resolving this upstream, replace the line below with:
# %%systemd_user_post bup-web.service
%systemd_post \\--user \\--global bup-web.service


%preun web
%systemd_user_preun bup-web.service


%postun web
%systemd_user_postun_with_restart bup-web.service


%files web
%doc bup-web/README.Fedora.md
%{_libdir}/%{name}/cmd/bup-web
%{_libdir}/%{name}/web/
%{_userunitdir}/bup-web.service
%{_mandir}/man1/bup-web.1*

%files
%doc README.md README.Fedora.md
%license LICENSE
%{_bindir}/%{name}
%{_libdir}/%{name}/
%exclude %{_libdir}/%{name}/cmd/bup-web
%exclude %{_libdir}/%{name}/web/
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*
%exclude %{_mandir}/man1/bup-web.1*


%changelog
* Fri Dec 04 2015 Tadej Janež <tadej.j@nez.si> 0.27-0.4
- Made bup-web subpackage Requires on the base package arch-specific.

* Mon Nov 23 2015 Tadej Janež <tadej.j@nez.si> 0.27-0.3
- Split bup web server into a separate sub-package.
- Added systemd service for running the bup web server.
- Added a work-around for a bug in systemd's %%systemd_user_post macro.
- Added a README with Fedora-specific notes on using the bup-web package.
- Converted the main README with Fedora-specific notes to Markdown.

* Wed Oct 14 2015 Tadej Janež <tadej.j@nez.si> 0.27-0.2
- Added perl(Time::HiRes) to BuildRequires since it is required for running the
  tests.
- Temporarily disable test_from_path_error() test that fails on Fedora Koji and
  COPR build systems.

* Sun May 17 2015 Tadej Janež <tadej.j@nez.si> 0.27-0.1
- Initial package.
