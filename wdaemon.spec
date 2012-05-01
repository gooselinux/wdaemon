%global evemu utouch-evemu-1.0.6

Name:		wdaemon
Version:	0.17
Release:	2%{?dist}
Summary:	Hotplug helper for Wacom X.org driver

Group:		User Interface/X
License:	GPLv3+
URL:		http://linuxwacom.sourceforge.net
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}

Source0:        http://prdownloads.sourceforge.net/linuxwacom/%{name}-%{version}.tar.bz2
Source1:        http://launchpad.net/utouch-evemu/trunk/v1.0.6/+download/%{evemu}.tar.gz

# RHEL6-special: needed to build evemu as static lib in subdir of wdaemon 
Patch001:       0001-Build-evemu-as-subdir-of-wdaemon.patch

# wacom driver doesn't exist on those
ExcludeArch:    s390 s390x

BuildRequires:  automake libtool
BuildRequires:  asciidoc xmlto
BuildRequires:  libudev-devel

%description
%{name} is daemon to provide static input devices for devices that may be
%hotplugged at runtime.

%prep
# wdaemon
%setup -q 
%patch001 -p1 -b .build-evemu-as-subdir

# evemu
%setup -T -a1 -D -q

%build
# build evemu first as static lib
pushd %{evemu}
autoreconf -v --install -f || exit 1
%configure --disable-shared
make %{?_smp_mflags}
popd

# now build wdaemon
export PKG_CONFIG_PATH=./%{evemu}
autoreconf -v --install -f || exit 1
%configure
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# remove evemu remainders
rm -f %{buildroot}/%{_bindir}/evemu-*
rm -f %{buildroot}/%{_includedir}/evemu.h
rm -f %{buildroot}/%{_libdir}/libutouch-evemu.*
rm -f %{buildroot}/%{_libdir}/pkgconfig/utouch-evemu.pc
rm -f %{buildroot}/%{_datadir}/man/man1/evemu-*.1*

%clean
rm -rf %{buildroot}

%post
if [ $1 = 1 ]; then
	/sbin/chkconfig --add %{name}
fi

%preun
if [ $1 = 0 ]; then
	/sbin/service %{name} stop > /dev/null 2>&1
	/sbin/chkconfig --del %{name}
fi

%postun
if [ $1 -ge 1 ]; then
	/sbin/service %{wdaemon} condrestart >dev/null 2>&1
fi

%files
%defattr(-,root,root,-)
%doc LICENSE conf/70-wdaemon-example.fdi

%{_bindir}/%{name}
%{_mandir}/man1/wdaemon.1*
/lib/udev/rules.d/60-wacom.rules
/lib/udev/rules.d/61-uinput-wacom.rules
/lib/udev/rules.d/61-uinput-stddev.rules
/lib/udev/wdaemon_is_uinput.sh
%config %{_sysconfdir}/rc.d/init.d/wdaemon

%changelog
* Tue Jul 26 2011 Peter Hutterer <peter.hutterer@redhat.com> 0.17-2
- Add %{?dist} to the release string.

* Wed Jun 22 2011 Peter Hutterer <peter.hutterer@redhat.com> 0.17-1
- Update to version 0.17 (#688003)
- build with evemu as static library

* Wed Aug 01 2007 Aristeu Rozanski <arozansk@redhat.com> 0.11-1
- Updated to version 0.11

* Tue Jul 24 2007 Aristeu S. Rozanski F. <arozansk@redhat.com> 0.10-3
- More problems found by Jarod Wilson fixed:
- Removing exclusive architectures, it used to be in sync with linuxwacom
  package
- marking udev rules as non-replaceable config files
- using install on makefile

* Mon Jul 23 2007 Aristeu S. Rozanski F. <arozansk@redhat.com> 0.10-2
- Fixing the problems found by Jarod Wilson:
- Fixing make install target
- Fixing Makefile so it honors the provided CFLAGS
- not using makeinstall macro
- installing is_uinput.sh as 755 instead of changing later with attr

* Fri Jul 20 2007 Aristeu S. Rozanski F. <arozansk@redhat.com> 0.10-1
* upgrading to version 0.10

* Thu Jul 19 2007 Aristeu S. Rozanski F. <arozansk@redhat.com> 0.09-1
- first release 

