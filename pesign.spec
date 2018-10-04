Summary:	Signing utility for UEFI binaries
Name:		pesign
Version:	0.112
Release:	1
Group:		Development/Other
License:	GPLv2
URL:		https://github.com/rhinstaller/pesign
Source0:	https://github.com/rhinstaller/pesign/releases/download/%{version}/%{name}-%{version}.tar.bz2
Source1:	certs.tar.xz
# (tpg) patches from Fedora
Patch0001: 0001-cms-kill-generate_integer-it-doesn-t-build-on-i686-a.patch
Patch0002: 0002-Fix-command-line-parsing.patch
Patch0003: 0003-gcc-don-t-error-on-stuff-in-includes.patch
Patch0004: 0004-Fix-certficate-argument-name.patch
Patch0005: 0005-Fix-description-of-ascii-armor-option-in-manpage.patch
Patch0006: 0006-Make-ascii-work-since-we-documented-it.patch
Patch0007: 0007-Switch-pesign-client-to-also-accept-token-cert-macro.patch
Patch0008: 0008-pesigcheck-Verify-with-the-cert-as-an-object-signer.patch
Patch0009: 0009-pesigcheck-make-certfile-actually-work.patch
Patch0010: 0010-signerInfos-make-sure-err-is-always-initialized.patch
Patch0011: 0011-pesign-make-pesign-h-tell-you-the-file-name.patch
Patch0012: 0012-Add-coverity-build-scripts.patch
Patch0013: 0013-Document-implicit-fallthrough.patch
Patch0014: 0014-Actually-setfacl-each-directory-of-our-key-storage.patch
Patch0015: 0015-oid-add-SHIM_EKU_MODULE_SIGNING_ONLY-and-fix-our-arr.patch
Patch0016: 0016-efikeygen-add-modsign.patch
Patch0017: 0017-check_cert_db-try-even-harder-to-pick-a-reasonable-v.patch
Patch0018: 0018-show-which-db-we-re-checking.patch
Patch0019: 0019-more-about-the-time.patch
Patch0020: 0020-try-to-say-why-something-fails.patch
Patch0021: 0021-Fix-race-condition-in-SEC_GetPassword.patch
Patch0022: 0022-sysvinit-Create-the-socket-directory-at-runtime.patch
Patch0023: 0023-Better-authorization-scripts.-Again.patch
Patch0024: 0024-Make-the-daemon-also-try-to-give-better-errors-on-EP.patch
Patch0025: 0025-certdb-fix-PRTime-printfs-for-i686.patch
Patch0026: 0026-Clean-up-gcc-command-lines-a-little.patch
Patch0027: 0027-Make-pesign-users-groups-static-in-the-repo.patch
Patch0028: 0028-rpm-Make-the-client-signer-use-the-fedora-values-unl.patch
Patch0029: 0029-Make-macros.pesign-error-in-kojibuilder-if-we-don-t-.patch
# Our own patches
Patch1000: pesign-0.112-pass-linker-flags-correctly.patch
BuildRequires:	pkgconfig(efivar)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	gnu-efi
BuildRequires:	nspr-devel
BuildRequires:	nss-devel
BuildRequires:	nss
BuildRequires:	popt-devel
BuildRequires:	opensc-devel
BuildRequires:	gcc gcc-c++
Requires:	nss
Requires:	popt
Requires:	rpm
Requires:	opensc
Requires(pre):	shadow
ExclusiveArch:	%{ix86} %{x86_64}

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q -T -b 0
%setup -q -T -D -c -n pesign-%{version}/ -a 1
%autopatch -p1

%build
#global optflags %{optflags} -Qunused-arguments -Wno-error=ignored-optimization-argument
#https://github.com/rhboot/pesign/issues/47
%make_build PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
mkdir -p %{buildroot}/%{_libdir}

make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} UNITDIR="/lib/systemd/system" install_systemd

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*

mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign/
mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/
cp -a etc/pki/pesign/* %{buildroot}%{_sysconfdir}/pki/pesign/
cp -a etc/pki/pesign-rh-test/* %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/

# (tpg) disable it for now
#OPENSC_DEBUG=9 /usr/bin/modutil -force -dbdir %{buildroot}/etc/pki/pesign -add opensc \
#	-libfile %{_libdir}/opensc-pkcs11.so

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
%doc README TODO
%doc %{_docdir}/%{name}-%{version}/COPYING
%{_bindir}/authvar
%{_bindir}/efisiglist
%{_bindir}/pesign
%{_bindir}/pesign-client
%{_bindir}/pesigcheck
%{_bindir}/efikeygen
%dir %{_sysconfdir}/pesign
%{_sysconfdir}/pesign/users
%{_sysconfdir}/pesign/groups
%{_sysconfdir}/popt.d/pesign.popt
%{_sysconfdir}/rpm/macros.d/pesign.macros
%{_mandir}/man*/*
%dir %attr(0775,pesign,pesign) /etc/pki/pesign
%attr(0664,pesign,pesign) /etc/pki/pesign/*
%dir %attr(0775,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/
%attr(0664,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/*
%dir %attr(0770, pesign, pesign) %{_localstatedir}/run/%{name}
%{_prefix}/lib/tmpfiles.d/pesign.conf
%{_unitdir}/pesign.service
%{_libexecdir}/pesign
