Summary:	Signing utility for UEFI binaries
Name:		pesign
Version:	0.108
Release:	1
Group:		Development/Other
License:	GPLv2
URL:		https://github.com/vathpela/pesign
BuildRequires:	git
BuildRequires:	gnu-efi
BuildRequires:	nspr
BuildRequires:	nss
BuildRequires:	nss-devel
BuildRequires:	popt-devel
BuildRequires:	coolkey
BuildRequires:	opensc
BuildRequires:	nspr-devel >= 4.9.2-1
BuildRequires:	nss-devel >= 3.13.6-1
Requires:	nspr
Requires:	nss
Requires:	nss-devel
Requires:	popt
Requires:	rpm
Requires:	coolkey
Requires:	opensc
Requires(pre): shadow
ExclusiveArch: %{ix86} x86_64
Source0: pesign-%{version}.tar.bz2

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q

%build
make PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
mkdir -p %{buildroot}/%{_libdir}

make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install_systemd

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*

modutil -force -dbdir %{buildroot}/etc/pki/pesign -add opensc \
	-libfile %{_libdir}/pkcs11/opensc-pkcs11.so

# rpm5 is cute
mkdir -p %{buildroot}%{_sysconfdir}/rpm/macros.d
mv %{buildroot}%{_sysconfdir}/rpm/macros.pesign %{buildroot}%{_sysconfdir}/rpm/macros.d/pesign.macros

# confusion due to fedora /lib == /usr/lib
mkdir -p %{buildroot}%{_unitdir}
mv %{buildroot}/usr/lib/systemd/system/*.service %{buildroot}%{_unitdir}

%pre
getent group pesign >/dev/null || groupadd -r pesign
getent passwd pesign >/dev/null || \
	useradd -r -g pesign -d /var/run/pesign -s /sbin/nologin \
		-c "Group for the pesign signing daemon" pesign
exit 0

%post
%systemd_post pesign.service

%preun
%systemd_preun pesign.service

%postun
%systemd_postun_with_restart pesign.service

%files
%doc README TODO COPYING
%{_bindir}/pesign
%{_bindir}/pesign-client
%{_bindir}/efikeygen
%{_sysconfdir}/popt.d/pesign.popt
%{_sysconfdir}/rpm/macros.d/pesign.macros
%{_mandir}/man*/*
%dir %attr(0775,pesign,pesign) /etc/pki/pesign
%attr(0664,pesign,pesign) /etc/pki/pesign/*
%dir %attr(0770, pesign, pesign) %{_localstatedir}/run/%{name}
%{_prefix}/lib/tmpfiles.d/pesign.conf
%{_unitdir}/pesign.service
