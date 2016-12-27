# render_template(src, dest):
# Renders the source template (using %%expand macro) and copies it to the
# destination path.
# Arguments:
#   - src: path of the source template to render
#   - dest: path of the destination file
%define render_template()\
if [[ %# -ne 2 ]]; then\
    echo "Invalid number of arguments to %0 macro: %#"\
    exit 1\
fi\
cat << 'EOF' > %2\
%{expand:%(cat %1)}\
EOF

%global commit0 d926749abdfe849117bf95c721d6f1858fef1d12
%global gittag0 0.28.1
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name: bup
Version: %{gittag0}
Release: 1%{?dist}
Summary: Very efficient backup system based on the git packfile format

# all of the code is licensed as GNU Lesser General Public License v2, except:
# - lib/bup/bupsplit.c: BSD License (two clause),
# - lib/bup/bupsplit.h: BSD License (two clause),
# - lib/bup/options.py: BSD License (two clause),
# - definition of relpath() function in wvtest.py: Python License
License: LGPLv2 and BSD and Python
URL: https://bup.github.io/
Source0: https://github.com/%{name}/%{name}/archive/%{gittag0}/%{name}-%{version}.tar.gz
Source1: README.Fedora.md
Source2: bup-web.service
Source3: README-bup-web.Fedora.md

BuildRequires: python2-devel
BuildRequires: git
# Required for building documentation
BuildRequires: pandoc
# Required for preparing systemd service for 'bup web' command
BuildRequires: systemd
# Required for running tests
BuildRequires: par2cmdline
BuildRequires: perl(Time::HiRes)
BuildRequires: pyxattr
BuildRequires: pylibacl
BuildRequires: python-tornado

Requires: git
Requires: pyxattr
Requires: pylibacl
# Only required for 'bup fuse' command
Requires: fuse-python
# Only required for 'bup fsck' command
Requires: par2cmdline


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
%autosetup


%build
# NOTE: We can't use %%configure since bup uses a non-standard configure script
# which is executed during the execution of the make command.
# To configure the build process, we need to pass variables to the make
# command.
%make_build CFLAGS="${CFLAGS:-%optflags}"

%render_template %{SOURCE1} %{_builddir}/%{buildsubdir}/README.Fedora.md
%render_template %{SOURCE3} %{_builddir}/%{buildsubdir}/README-bup-web.Fedora.md


%install
# NOTE: Since bup uses a non-standard configure script, which doesn't support
# specifying distro-specific paths of the variables defined below, we need to
# manually pass variables to the make command.
%make_install \
    PREFIX=%{_prefix} \
    MANDIR=%{_mandir} \
    DOCDIR=%{_pkgdocdir} \
    BINDIR=%{_bindir} \
    LIBDIR=%{_libdir}/%{name}

# Fix hard-coded libdir location in bup's executable
sed -i 's|/lib/bup|/%{_lib}/bup|' %{buildroot}%{_bindir}/bup

# Install systemd unit file
mkdir -p %{buildroot}%{_userunitdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_userunitdir}

# Install READMEs and Notable changes manually
# NOTE: This is necessary since mixing the %%doc with relative paths and
# installation of files directly into %%_pkgdocdir in the same source package
# is forbidden. For more details, see:
# https://fedoraproject.org/wiki/Packaging:Guidelines#Documentation
install -p -m 0644 README.md %{buildroot}%{_pkgdocdir}
install -p -m 0644 README*.Fedora.md %{buildroot}%{_pkgdocdir}
install -p -m 0644 note/*.md %{buildroot}%{_pkgdocdir}


%check
# Run the built-in test suite containing 4200+ tests
%make_build test


%post web
%if 0%{?fedora} >= 24
%systemd_user_post bup-web.service
%else
# NOTE: %%systemd_user_post macro is broken in systemd < v229, hence we need
# this work-around.
%systemd_post \\--user \\--global bup-web.service
%endif


%preun web
%systemd_user_preun bup-web.service


%postun web
%systemd_user_postun_with_restart bup-web.service


%files web
%{_libdir}/%{name}/cmd/bup-web
%{_libdir}/%{name}/web/
%{_userunitdir}/bup-web.service
%{_mandir}/man1/bup-web.1*
%{_pkgdocdir}/bup-web.html
%{_pkgdocdir}/README-bup-web.Fedora.md

%files
%license LICENSE
%{_bindir}/%{name}
%{_libdir}/%{name}/
%exclude %{_libdir}/%{name}/cmd/bup-web
%exclude %{_libdir}/%{name}/web/
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*
%exclude %{_mandir}/man1/bup-web.1*
%{_pkgdocdir}/
%exclude %{_pkgdocdir}/bup-web.html
%exclude %{_pkgdocdir}/README-bup-web.Fedora.md


%changelog
* Tue Dec 27 2016 Tadej Janež <tadej.j@nez.si> 0.28.1-1
- Updated to 0.28.1 release.
- Enabled 'par2' support in 'bup fsck'.
- Made tests run in parallel.
- Packaged HTML documentation.
- Dropped all patches.
- Updated and modernized spec file:
  - Use %%make_build macro.
  - Use %%make_install macro.
  - Simplify %%make_install part since bup now properly implements DESTDIR
    environment variable.
  - Stop mixing the %%doc with relative paths and installation of files
    directly into %%_pkgdocdir.
  - Use %%systemd_user_post macro on Fedora 24+.
  - Implement and use %%render_template macro to render READMEs containing
    RPM macros using %%expand macro.
  - Add additional BuildRequires needed by tests.
  - Follow the latest SourceURL packaging guidelines and reference git tag
    instead of commit revision in Source0 URL.
  - Drop special prerelease handling.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.27-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 14 2015 Tadej Janež <tadej.j@nez.si> 0.27-1
- Initial release in Fedora 22+ and EPEL 7.
- Added a workaround for an %%autosetup bug on EPEL 7.

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
