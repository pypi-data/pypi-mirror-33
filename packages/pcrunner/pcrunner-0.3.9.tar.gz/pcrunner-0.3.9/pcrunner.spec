%global name pcrunner
%global version 0.3.9
%global release 1

%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7)

Summary: Pcrunner (Passive Check Runner)
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: ISCL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Maarten <ikmaarten@gmail.com>
Url: https://github.com/maartenq/pcrunner
%if %{use_systemd}
Requires: systemd
BuildRequires: systemd
%else
Requires(postun): initscripts
Requires(post): chkconfig
Requires(preun): chkconfig
%endif
Requires: python-setuptools,python-argparse,PyYAML

%description
Pcrunner, Passive Checks Runner, is a daemon and service that periodically runs
Nagios_ / Icinga_ checks paralell. The results are posted via HTTPS to a
`NSCAweb`_ server.


* Free software: ISC license
* Documentation: https://pcrunner.readthedocs.io/en/latest/

Features
--------

* Runs as a daemon on Linux.
* Runs as a service on win32.
* Command line interface for single test runs and/or cron use.
* Parallel execution of check commands.
* Posts check results external commands.
* Termniation of check commands if maximum time exceeds.
* Configuration in YAML.
* Command definition in YAML or text format.


Installation
------------

http://pcrunner.readthedocs.io/en/latest/installation.html


.. _NSCAweb: https://github.com/smetj/nscaweb
.. _Nagios: http://www.nagios.org/
.. _Icinga: http://www.icinga.org/


%prep
%setup -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 \
    --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
%{__mkdir} -p %{buildroot}/var/spool/pcrunner
%{__mkdir} -p %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 0644 %{name}/etc/commands.txt \
    %{buildroot}%{_sysconfdir}/%{name}/commands.txt
%{__install} -m 0644 %{name}/etc/commands.yml \
    %{buildroot}%{_sysconfdir}/%{name}/commands.yml
%{__install} -m 0640 %{name}/etc/pcrunner.yml \
    %{buildroot}%{_sysconfdir}/%{name}/pcrunner.yml

%if %{use_systemd}
# install systemd-specific files
%{__mkdir} -p %{buildroot}%{_unitdir}
%{__install} -m 0644 systemd/%{name}.service \
    %{buildroot}%{_unitdir}/%{name}.service
%else
# install SYSV init stuff
%{__install} -m 0755 init/%{name} %{buildroot}%{_initrddir}/%{name}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{use_systemd}
    /usr/bin/systemctl preset %{name}.service >/dev/null 2>&1 ||:
%else
    /sbin/chkconfig --add %{name}
    /sbin/chkconfig %{name} on
%endif

%preun
%if %{use_systemd}
    /usr/bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
    /usr/bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
%else
if [ "$1" = "0" ]; then
    /sbin/service %{name} stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del %{name}
fi
%endif

%postun
if [ "$1" -ge "1" ]; then
%if %{use_systemd}
    /usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
%else
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
%endif

%files -f INSTALLED_FILES
%defattr(-,root,root)
%attr(0755,root,root) /var/spool/pcrunner
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/commands.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/commands.yml
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/%{name}/pcrunner.yml
%if %{use_systemd}
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%endif

%changelog
* Fri Jul 14 2018 Maarten <ikmaarten@gmail.com> - 0.3.9-1
- Added systemd service file for Fedora >=18 Centos >=7
* Fri Feb  9 2018 Maarten <ikmaarten@gmail.com> - 0.3.8-1
- Fix: issue #83
* Fri Nov 17 2017 Maarten <ikmaarten@gmail.com> - 0.3.7-1
- Fix: quotes in commands.txt and commands.txt seem to get ignored #82
* Fri Nov 17 2017 Maarten <ikmaarten@gmail.com> - 0.3.6-1
- dev requirements updates
* Fri Dec 09 2016 Maarten <ikmaarten@gmail.com> - 0.3.5-1
- dev requirements updates
- docs usage
* Fri Nov 18 2016 Maarten <ikmaarten@gmail.com> - 0.3.4-1
- dev requirements updates
* Fri Nov 11 2016 Maarten <ikmaarten@gmail.com> - 0.3.3-1
- dev requirements updates
- docs: download from `GitHub`
* Fri Oct 14 2016 Maarten <ikmaarten@gmail.com> - 0.3.2-1
- dev requirements updates
* Fri Sep 30 2016 Maarten <ikmaarten@gmail.com> - 0.3.1-1
- dev requirements updates
* Fri Sep 09 2016 Maarten <ikmaarten@gmail.com> - 0.3.0-1
- Added `--no-daemon` option for starting pcrunner's run loop in foreground.
- dev requirements updates
* Fri Aug 26 2016 Maarten <ikmaarten@gmail.com> - 0.2.10-1
- tox.ini updated
- removed specific version for package requirements from setup.py.
- readthedocs theme for local docs build.
- OS-X and vim files in .gitignore
- Update requirements: pytest -> 3.0.1
* Sat Aug 20 2016 Maarten <ikmaarten@gmail.com> - 0.2.8-1
- Updated docs
* Sat Aug 20 2016 Maarten <ikmaarten@gmail.com> - 0.2.7-1
- Updated project links.
* Sat Aug 20 2016 Maarten <ikmaarten@gmail.com> - 0.2.6-1
- Fixed ISSUE#4: commands file with extra white lines.
* Sat Aug 20 2016 Maarten <ikmaarten@gmail.com> - 0.2.5-1
- Updated Python installation documentation with new versions.
* Sat Aug 13 2016 Maarten <ikmaarten@gmail.com> - 0.2.4-1
- xrange -> range for python3 compatibility.
* Sat Aug 13 2016 Maarten <ikmaarten@gmail.com> - 0.2.3-1
- Travis/tox fix
* Sat Aug 13 2016 Maarten <ikmaarten@gmail.com> - 0.2.2-1
-  ISC License
* Sat Aug 13 2016 Maarten <ikmaarten@gmail.com> - 0.2.1-1
- Documentation RPM build updated.
* Fri Aug 12 2016 Maarten <ikmaarten@gmail.com> - 0.2.0-1
- First release on PyPI.
