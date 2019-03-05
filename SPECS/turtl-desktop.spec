# turtl-desktop.spec
# vim:tw=0:ts=2:sw=2:et:
#
# Turl - The Secure Collaborative Notebook
#        Encrypted notes. Includes markdown support.
#
# https://github/taw00/turtl-rpm
# https://copr.fedorainfracloud.org/coprs/taw/turtl
#
# https://turtlapp.com/
# https://github.com/turtl

# ---

# Package (RPM) name-version-release.
# <name>-<vermajor.<verminor>-<pkgrel>[.<extraver>][.<snapinfo>].DIST[.<minorbump>]

Name: turtl-desktop
Summary: The Secure Collaborative Notebook

%define targetIsProduction 0

# ie. if the dev team (or I in this case) includes things like rc3 or the
# date in the source filename
%define buildQualifier 20190226
%define nwjs_version 0.36.2

# VERSION - can edit this
# eg. 0.17.0
%define vermajor 0.7
%define verminor 2.5
Version: %{vermajor}.%{verminor}

# RELEASE - can edit this
%define _pkgrel 1
%if ! %{targetIsProduction}
  %define _pkgrel 0.1
%endif

# MINORBUMP - can edit this
%define minorbump taw1

#
# Build the release string - don't edit this
#

%define snapinfo testing
%if %{targetIsProduction}
  %undefine snapinfo
%endif
%if 0%{?buildQualifier:1}
  %define snapinfo %{buildQualifier}
%endif

# pkgrel will also be defined, snapinfo and minorbump may not be
%define _release %{_pkgrel}
%if 0%{?snapinfo:1}
  %if 0%{?minorbump:1}
    %define _release %{_pkgrel}.%{snapinfo}%{?dist}.%{minorbump}
  %else
    %define _release %{_pkgrel}.%{snapinfo}%{?dist}
  %endif
%else
  %if 0%{?minorbump:1}
    %define _release %{_pkgrel}%{?dist}.%{minorbump}
  %else
    %define _release %{_pkgrel}%{?dist}
  %endif
%endif

Release: %{_release}
# ----------- end of release building section

# https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing
# Apache Software License 2.0
License: GPL 3.0
URL: https://turtlapp.com
# Note, for example, this will not build on ppc64le
ExclusiveArch: x86_64 i686 i586 i386

# how are debug info and build_ids managed (I only halfway understand this):
# https://github.com/rpm-software-management/rpm/blob/master/macros.in
# ...flip-flop next two lines in order to disable (nil) or enable (1) debuginfo package build
%define debug_package 1
%define debug_package %{nil}
%define _unique_build_ids 1
%define _build_id_links alldebug

# https://fedoraproject.org/wiki/Changes/Harden_All_Packages
# https://fedoraproject.org/wiki/Packaging:Guidelines#PIE
%define _hardened_build 1

# https://fedoraproject.org/wiki/Packaging:SourceURL
# Sources as part of source RPM can be found at
#   https://github.com/taw00/turtl-rpm
%define _repo_archive %{name}-%{version}-%{buildQualifier}
%define _source0_name desktop
%define _source0 %{_source0_name}-%{version}
%define _source1_name core
%define _source1 %{_source1_name}-rs
%define _source2 js
%define _source4 %{name}-%{vermajor}-contrib

Source0: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{_repo_archive}/%{_source0}.tar.gz
Source1: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{_repo_archive}/%{_source1}.tar.gz
Source2: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{_repo_archive}/%{_source2}.tar.gz
Source3: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{name}.appdata.xml
#Source4: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%%{_repo_archive}/%%{name}-%%{vermajor}-contrib.tar.gz

BuildRequires: nodejs npm git
BuildRequires: openssl-libs openssl-devel
BuildRequires: rust cargo libsodium-static
BuildRequires: curl rsync
# Required of node ffi
BuildRequires: python2 gcc-c++
# provided by coreutils RPM
#BuildRequires: /usr/bin/readlink /usr/bin/dirname

BuildRequires: desktop-file-utils
%if 0%{?suse_version:1}
BuildRequires: appstream-glib
#BuildRequires: libappstream-glib8 appstream-glib
%else
BuildRequires: libappstream-glib
%endif

#t0dd: I will often add tree, vim-enhanced, and less for mock environment
#      introspection
%if ! %{targetIsProduction}
BuildRequires: tree vim-enhanced less findutils dnf
%endif



# Unarchived source tree structure (extracted in {_builddir})
#   sourceroot            turtl-desktop-0.7-20190226
#    \_{_source0}             \_desktop-0.7.2.5 (renamed to desktop)
#    \_{_source1}             \_core-rs (renamed to core)
#    \_{_source2}             \_js
#NOTYET\_sourcecontribtree  \_turtl-desktop-0.7-contrib
#%%define sourcecontribtree %%{name}-%%{vermajor}-contrib
%define sourceroot %{name}-%{vermajor}-%{buildQualifier}
# /usr/share/turtl-desktop
%define installtree %{_datadir}/%{name}


%description
Turtl is a free and secure collaborative markdown-enabled notebook web
application. turtl-desktop serves as a desktop frontend to a turtl-server.

By default, notes are syncronized with turtlapp.com. Users or organizations may
also host their own turtlapp servers to use as secure and privately managed
targets for user and team notes (see also the turtl-server RPM).

%prep
# Prep section starts us in directory {_builddir}
# Extract into {_builddir}/{sourceroot}/
# FYI: Each "setup" leaves you in the {sourceroot} directory
rm -rf %{sourceroot} ; mkdir -p %{sourceroot}
# Source0:...
%setup -q -T -D -a 0 -n %{sourceroot}
cd .. ; mv -v %{sourceroot}/%{_source0} %{sourceroot}/%{_source0_name}
# Source1:...
%setup -q -T -D -a 1 -n %{sourceroot}
cd .. ; mv -v %{sourceroot}/%{_source1} %{sourceroot}/%{_source1_name}
# Source2:...
%setup -q -T -D -a 2 -n %{sourceroot}
# Source3:...
cd .. ; cp ../SOURCES/%{name}.appdata.xml %{sourceroot}/ ; cd %{sourceroot}
# Source4:...
#%%setup -q -T -D -a 4 -n %%{sourceroot}
cd ..

# Make sure the right library path is used...
#echo "%%{_libdir}/%%{name}" > %%{sourcecontribtree}/etc-ld.so.conf.d_%%{name}.conf

# extract the rest of the tree
cd %{sourceroot}
# nwjs
# https://github.com/nwjs/nw.js/releases
%if "%{?_lib}" == "lib64"
  %define _nwjs_dir nwjs-v%{nwjs_version}-linux-x64
%else
  %define _nwjs_dir nwjs-v%{nwjs_version}-linux-ia32
%endif
#/usr/bin/curl -LO# https://dl.nwjs.io/v%{nwjs_version}/%{_nwjs_dir}.tar.gz
#/usr/bin/curl -LO# https://toddwarner.keybase.pub/pub/srpms/build_support/%{_nwjs_dir}.tar.gz
/usr/bin/curl -LOs https://toddwarner.keybase.pub/pub/srpms/build_support/%{_nwjs_dir}.tar.gz
tar xvzf %{_nwjs_dir}.tar.gz
%define _nwjs_path $(readlink -e %{_nwjs_dir})
echo "\
export PATH := $(PATH):%{_nwjs_path}:%{_builddir}/%{sourceroot}/core
export RUSTFLAGS := -L%{_libdir}
export SODIUM_LIB_DIR := %{_libdir}
export SODIUM_STATIC := static
export OPENSSL_LIB_DIR=%{_libdir}
export OPENSSL_INCLUDE_DIR=%{_includedir}/openssl
" > core/var.mk
cd ..

# For debugging purposes...
%if ! %{targetIsProduction}
#cd .. ; tree -df -L 2 %{sourceroot} ; cd -
cd .. ; tree -d -L 2 %{sourceroot} ; cd -
%endif


%build
# Build section starts us in directory {_builddir}/{sourceroot}

# Clearing npm's cache and package lock to eliminate SHA1 integrity issues.
#%%{warn: "taw build note: I keep running into this fatal error --'integrity checksum failed when using sha1'. Taking dramatic action -brute force- in an attempt to remedy it.' If someone can figure out what is causing this, I will buy them a beer."}
/usr/bin/npm cache clean --force
rm -rf ${HOME}/.npm/_cacache
#rm -f package-lock.json

%if 0%{?suse_version:1}
  # We trust where we are getting modules from and Suse builds require
  # https-agnostism apparently (I don't know why) -t0dd
  /usr/bin/npm config set strict-ssl false
  /usr/bin/npm config set registry http://registry.npmjs.org/
  #/usr/bin/npm config set registry http://matrix.org/packages/npm/
  /usr/bin/npm config list
%endif

/usr/bin/npm install
/usr/bin/npm audit fix
%if 0%{?suse_version:1}
  /usr/bin/sleep 15
%endif

# core
cd core
make
cd ..

# js
cd js
/usr/bin/npm install
/usr/bin/npm audit fix
cp config/config.js.default config/config.js
cd ..

# desktop
cd desktop
#/usr/bin/npm cache clean --force
/usr/bin/npm install electron@3
/usr/bin/npm install electron-context-menu
/usr/bin/npm install electron-store
#/usr/bin/npm install coffee
PYTHON=/usr/bin/python2 /usr/bin/npm install ffi
/usr/bin/npm install --save-dev electron-rebuild
/usr/bin/npm install --save-dev electron-packager
/usr/bin/npm install
/usr/bin/npm audit fix
make electron-rebuild
make
/usr/bin/npm audit fix
make release-linux


%install
# Install section starts us in directory {_builddir}/{sourceroot}

# Cheatsheet for some built-in RPM macros:
# https://fedoraproject.org/wiki/Packaging:RPMMacros
#   _builddir = {_topdir}/BUILD
#   _buildrootdir = {_topdir}/BUILDROOT
#   buildroot = {_buildrootdir}/{name}-{version}-{release}.{_arch}
#   _datadir = /usr/share
#   _mandir = /usr/share/man
#   _sysconfdir = /etc
#   _libdir = /usr/lib or /usr/lib64 (depending on system)

# Create directories
install -d %{buildroot}%{_libdir}/%{name}
install -d -m755 -p %{buildroot}%{_bindir}
install -d %{buildroot}%{installtree}
install -d %{buildroot}%{_datadir}/applications
%define _metainfodir %{_datadir}/metainfo
install -d %{buildroot}%{_metainfodir}

echo "[Desktop Entry]
Type=Application
Name=Turtl
GenericName=Secure notes
Comment=The secure collaborative notebook
Exec=%{name}
Icon=%{name}
Terminal=false
Categories=Office;
Keywords=secure;security;privacy;private;notes;bookmarks;collaborate;research;
StartupNotify=true
X-Desktop-File-Install-Version=0.23
" > %{buildroot}%{_datadir}/applications/%{name}.desktop
install -D -m644 -p desktop/scripts/resources/favicon.128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
install -D -m644 -p %{name}.appdata.xml %{buildroot}%{_metainfodir}/%{name}.appdata.xml
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.appdata.xml

cd desktop/target/Turtl*
# Nuke a particlarly troublesome unneeded but included electron components...
rm -rf resources/app/node_modules/performance-now
# This is horrible brute-force logic...
# ...Save only the components that matter (according to upstream builds)
#%%define _blessed_apps "bindings conf debug dot-prop electron-context-menu electron-dl electron-is-dev electron-store env-paths ext-list ext-name ffi graceful-fs imurmurhash is-obj is-plain-obj make-dir mime-db modify-filename ms nan pkg-up pupa ref ref-struct signal-exit sort-keys sort-keys-length @types unused-filename write-file-atomic"
#cd resources/app/
#cp -a node_modules node_modules_remove
#cd node_modules_remove
#mv -v %%{_blessed_apps} ../node_modules/
#cd ..
#rm -rf node_modules_remove
#cd ../..
cp -a . %{buildroot}%{installtree}/

# a little ugly - symbolic link creation
ln -s %{installtree}/turtl %{buildroot}%{_bindir}/%{name}


%files
%defattr(-,root,root,-)
%license %{installtree}/LICENSE
%{_bindir}/*
%{_datadir}/icons/*
%{_datadir}/applications/%{name}.desktop
%{_metainfodir}/%{name}.appdata.xml
# We own /usr/share/turtl-desktop and everything under it...
%{installtree}


%post
umask 007
#/sbin/ldconfig > /dev/null 2>&1
/usr/bin/update-desktop-database &> /dev/null || :


%postun
umask 007
#/sbin/ldconfig > /dev/null 2>&1
/usr/bin/update-desktop-database &> /dev/null || :


%changelog
* Mon Mar 04 2019 Todd Warner <t0dd_at_protonmail.com> 0.7.2.5-20190226.testing.taw2
  - minor tweaks to descriptions and such.

* Sun Mar 03 2019 Todd Warner <t0dd_at_protonmail.com> 0.7.2.5-20190226.testing.taw1
  - npm audit fix added as suggested by the build

* Sat Mar 02 2019 Todd Warner <t0dd_at_protonmail.com> 0.7.2.5-20190226.testing.taw
  - v0.7.2.5 as of 20190226
