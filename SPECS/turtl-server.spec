# turtl-server.spec
# vim:tw=0:ts=2:sw=2:et:
#
# Turtl - The Secure Collaborative Notebook
#         End-to-end encrypted markdown. Syncable. Shareable.
#
# Turtl Server -- A backend self-hostable Turtl orchestration server.
#
# The RPM builds...
# https://github/taw00/turtl-rpm
# https://copr.fedorainfracloud.org/coprs/taw/turtl
#
# The upstream project...
# https://turtlapp.com/
# https://github.com/turtl

# ---

# Package (RPM) name-version-release.
# <name>-<vermajor.<verminor>-<pkgrel>[.<extraver>][.<snapinfo>].DIST[.<minorbump>]

Name: turtl-server
Summary: The Secure Collaborative Notebook (server component)

%define targetIsProduction 0

# ie. if the dev team (or I in this case) includes things like rc3 or the
# date in the source filename
%define buildQualifier 20190524
#%%undefine buildQualifier

# VERSION
%define vermajor 0.0
%define verminor 0
Version: %{vermajor}.%{verminor}

# RELEASE
# package release, and potentially extrarel
%define _pkgrel 1
%if ! %{targetIsProduction}
  %define _pkgrel 0.10
%endif

# MINORBUMP
%define minorbump taw
#%%undefine minorbump

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

%define _hardened_build 1

%if 0%{?buildQualifier:1}
Source0: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{name}-%{version}-%{buildQualifier}.tar.gz
%else
Source0: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{name}-%{version}.tar.gz
%endif
Source1: https://github.com/taw00/turtl-rpm/blob/master/SOURCES/%{name}-%{vermajor}-contrib.tar.gz

Requires: nodejs postgresql-server postgresql-contrib
# These are suggested, not required...
#Requires: webserver openssl
BuildRequires: nodejs npm git
BuildRequires: systemd
%{?systemd_requires}

# I will often add these packages for mock environment introspection
%if ! %{targetIsProduction}
BuildRequires: tree vim-enhanced less findutils
%endif

# Unarchived source tree structure (extracted in {_builddir})
#   sourceroot            turtl-server-0.0
#    \_sourcetree           \_turtl-server-0.0.0-20190302
%define sourceroot %{name}-%{vermajor}
%if 0%{?buildQualifier:1}
%define sourcetree %{name}-%{version}-%{buildQualifier}
%else
%define sourcetree %{name}-%{version}
%endif
%define sourcecontribtree %{name}-%{vermajor}-contrib
# /usr/share/turtl-server
%define installtree %{_datadir}/%{name}


%description
Turtl is a free and secure collaborative markdown-enabled notebook web
application backend for the turtle-desktop app (or mobile app). turtl-server
deploys the components of the server-side web application.

Turtl Server is a self-hostable communication and sychronization hub enabling
users to synchronize their Turtl client data across all of their devices and
collaborate with other users on the network. As part of the sychronization
process, a Turtl Server also serves as a secure backup of user content. All
data is secured with end-to-end encryption.


%prep
# Prep section starts us in directory {_builddir}
# Extract into {_builddir}/{sourceroot}/
# Each "setup" leaves you in the {sourceroot} directory
rm -rf %{sourceroot} ; mkdir -p %{sourceroot}
# Source0:...
%setup -q -T -D -a 0 -n %{sourceroot}
# Source1:...
%setup -q -T -D -a 1 -n %{sourceroot}

# For debugging purposes...
%if ! %{targetIsProduction}
cd .. ; tree -d -L 2 %{sourceroot} ; cd -
%endif


%build
# Build section starts us in directory {_builddir}/{sourceroot}

# Clearing npm's cache and package lock to eliminate SHA1 integrity issues.
/usr/bin/npm cache clean --force
rm -rf ${HOME}/.npm/_cacache
#rm -f package-lock.json

cp %{sourcecontribtree}/config.yaml.default %{sourcetree}/config/config.yaml.default_rpm_supplied
cp %{sourcecontribtree}/config.yaml.default %{sourcetree}/config/config.yaml

cd %{sourcetree}
/usr/bin/npm install 
/usr/bin/npm audit fix

# Can't install pm2 because requires /sbin/openrc-run which is not available
# for Fedora that I can tell
#/usr/bin/npm install pm2@latest

# Nuke a particlarly troublesome unneeded but included electron components...
# Apparently "uninstall" just won't remove it. Grr.
#/usr/bin/npm uninstall performance-new
rm -rf node_modules/performance-now
cd ..


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
#   _sharedstatedir is /var/lib
#   _libdir = /usr/lib or /usr/lib64 (depending on system)
%define _rawlib lib
%define _usr_lib /usr/%{_rawlib}
# These three are already defined in newer versions of RPM, but not in el7
%if 0%{?rhel} && 0%{?rhel} < 8
%define _tmpfilesdir %{_usr_lib}/tmpfiles.d
%define _unitdir %{_usr_lib}/systemd/system
%define _metainfodir %{_datadir}/metainfo
%endif


# Create directories
install -d -m755 -p %{buildroot}%{_bindir}
# /usr/share/turtl-server/...
install -d %{buildroot}%{installtree}
install -d %{buildroot}%{installtree}/plugins
# /var/lib/turtl-server/...
install -d %{buildroot}%{_sharedstatedir}
install -d -m750 -p %{buildroot}%{_sharedstatedir}/%{name}/public/uploads
# /var/log/turtl-server/...
install -d -m750 %{buildroot}%{_localstatedir}/log/%{name}
# ...logrotate file rules
install -D -m644 -p %{sourcecontribtree}/etc-logrotate.d_turtl-server %{buildroot}/etc/logrotate.d/%{name}
# ...ghosted log files - need to exist in the installed buildroot
touch %{buildroot}%{_localstatedir}/log/%{name}/%{name}.log

# Create directories (systemd stuff)
# /usr/lib/systemd/system/
install -d %{buildroot}%{_unitdir}
# /etc/sysconfig/turtl-serverd-scripts/
install -d %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts
# /usr/lib/tmpfiles.d/
install -d %{buildroot}%{_tmpfilesdir}

# firewalld services
install -D -m644 -p %{sourcecontribtree}/usr-lib-firewalld-services_turtl-server.xml %{buildroot}%{_usr_lib}/firewalld/services/turtl-server.xml

# systemd services
install -D -m750 -p %{sourcecontribtree}/systemd/usr-share-turtl-server_turtl-serverd-start.sh %{buildroot}%{installtree}/turtl-serverd-start.sh
install -D -m600 -p %{sourcecontribtree}/systemd/etc-sysconfig_%{name}d %{buildroot}%{_sysconfdir}/sysconfig/%{name}d
install -D -m755 -p %{sourcecontribtree}/systemd/etc-sysconfig-%{name}d-scripts_send-email.sh %{buildroot}%{_sysconfdir}/sysconfig/%{name}d-scripts/send-email.sh
install -D -m644 -p %{sourcecontribtree}/systemd/usr-lib-systemd-system_%{name}d.service %{buildroot}%{_unitdir}/%{name}d.service
install -D -m644 -p %{sourcecontribtree}/systemd/usr-lib-tmpfiles.d_%{name}d.conf %{buildroot}%{_tmpfilesdir}/%{name}d.conf

# other
install -D -m644 -p %{sourcecontribtree}/README-turtl-server.md %{buildroot}%{installtree}/
install -D -m770 -p %{sourcecontribtree}/backup-*.sh %{buildroot}%{installtree}/
install -D -m770 -p %{sourcecontribtree}/_backup-*.sh %{buildroot}%{installtree}/


cd %{sourcetree}
cp -a . %{buildroot}%{installtree}/


%files
%defattr(-,root,turtl,-)
%config(noreplace) %attr(660,root,turtl) %{installtree}/config/config.yaml
# We own /usr/share/turtl-server and everything under it...
# Going to throw warnings in the RPM build because we already pulled in LICENSE and config.yaml
%{installtree}
# /var/lib...
%dir %attr(750,turtl,turtl) %{_sharedstatedir}/%{name}
%attr(-,turtl,turtl) %{_sharedstatedir}/%{name}/*
# /var/log...
%dir %attr(750,turtl,turtl) %{_localstatedir}/log/%{name}
# /etc/sysconfig/turtl-serverd-scripts/
%dir %attr(755,turtl,turtl) %{_sysconfdir}/sysconfig/%{name}d-scripts

%defattr(-,root,root,-)
%license %{installtree}/LICENSE
%doc %{sourcecontribtree}/README-turtl-server.md
# firewalld service definition
%{_usr_lib}/firewalld/services/turtl-server.xml
# systemd service definition
%{_unitdir}/%{name}d.service
# systemd service tmp file
%{_tmpfilesdir}/%{name}d.conf
# systemd service config and scripts
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/sysconfig/%{name}d
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}d-scripts/send-email.sh

# Logs
# log file - doesn't initially exist, but we still own it
%ghost %{_localstatedir}/log/%{name}/%{name}.log
%attr(644,root,root) %{_sysconfdir}/logrotate.d/%{name}


##
## Installing/Uninstalling the RPM: pre, post, posttrans, preun, postun
##


%pre
# _sharedstatedir is /var/lib
getent group turtl >/dev/null || groupadd -r turtl
getent passwd turtl >/dev/null || useradd -r -g turtl -d %{_sharedstatedir}/%{name} -s /sbin/nologin -c "System user 'turtl' to isolate turtl server activities" turtl


%post
umask 007
# refresh systemd context
%systemd_post %{name}d.service
# refresh firewalld context
#%%firewalld_reload
test -f %{_bindir}/firewall-cmd && firewall-cmd --reload --quiet || true


%preun
# systemd stuff
%systemd_preun %{name}d.service


%postun
umask 007
# refresh firewalld context
#%%firewalld_reload
test -f %{_bindir}/firewall-cmd && firewall-cmd --reload --quiet || true


%posttrans
/usr/bin/systemd-tmpfiles --create


%changelog
* Tue Jun 11 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.10.20190524.taw
  - _backup*.sh -- backup helper script was never included. Oops!
  - fixed default webroot in backup script comments

* Fri May 24 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.9.20190524.taw
  - updated to repo as of 2019-05-24

* Fri Apr 19 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.8.20190419.taw
  - updated to repo as of 2019-04-19

* Sun Mar 10 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.7.20190303.taw
  - lots of relatively trivial changes, primarily to documentation & comments.

* Thu Mar 07 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.6.20190303.taw
* Thu Mar 07 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.5.20190303.taw
* Thu Mar 07 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.4.20190303.taw
* Thu Mar 07 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.3.20190303.taw
* Thu Mar 07 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.2.20190303.taw
  - Updated config-file documentation. Some consistency fixes as well.
  - config.yaml, which is permissioned to root:turtl changed from 0640 to 0660
  - added firewalld service definition in case you want to export 8181 directly
  - added README to the contribution tarball
  - added instruction for telling nginx to stream to turtl server, otherwise  
    nginx will suck down the entire blob and THEN send to turtl server. Ugly.
  - firewalld_reload macro is non-functional for some reason
  - you don't *need* a webserver to run a Turtl Server, therefore, I removed  
    the requirement.
  - added a backup script

* Tue Mar 05 2019 Todd Warner <t0dd_at_protonmail.com> 0.0.0-0.1.20190303.taw
  - state of upstream repo as of 20190303

