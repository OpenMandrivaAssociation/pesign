Summary:	Signing utility for UEFI binaries
Name:		pesign
Version:	0.110
Release:	1
Group:		Development/Other
License:	GPLv2
URL:		https://github.com/rhinstaller/pesign
Source0:	https://github.com/rhinstaller/pesign/releases/download/%{version}/%{name}-%{version}.tar.bz2
Patch0:		pesign-efivar-pkgconfig.patch
Patch1:		pesign-make-efi_guid_t-const.patch
BuildRequires:	pkgconfig(efivar)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	gnu-efi
BuildRequires:	nspr-devel
BuildRequires:	nss-devel
BuildRequires:	nss
BuildRequires:	popt-devel
BuildRequires:	opensc-devel
Requires:	nss
Requires:	popt
Requires:	rpm
Requires:	opensc
Requires(pre):	shadow
ExclusiveArch:	%{ix86} x86_64

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q
%apply_patches

%build
%make PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
mkdir -p %{buildroot}/%{_libdir}

make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} UNITDIR="/lib/systemd/system" install_systemd

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*

OPENSC_DEBUG=9 /usr/bin/modutil -force -dbdir %{buildroot}/etc/pki/pesign -add opensc \
	-libfile %{_libdir}/opensc-pkcs11.so

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
