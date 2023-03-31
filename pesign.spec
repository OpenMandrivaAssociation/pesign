Summary:	Signing utility for UEFI binaries
Name:		pesign
Version:	115
Release:	2
Group:		Development/Other
License:	GPLv2
URL:		https://github.com/rhinstaller/pesign
Source0:	https://github.com/rhinstaller/pesign/releases/download/%{version}/%{name}-%{version}.tar.bz2
Source1:	certs.tar.xz
# (tpg) patches from Fedora
Patch0001:	0001-daemon-remove-always-true-comparison.patch
Patch0002:	0002-make-handle-some-gcc-Wanalyzer-flags-better.patch
Patch0003:	0003-Rename-dprintf-to-dbgprintf.patch
Patch0004:	0004-.gitignore-add-compile_commands.json-and-.cache.patch
Patch0005:	0005-pesign-print-digests-before-filenames-like-sha256sum.patch
Patch0006:	0006-Add-pesum-an-authenticode-digest-generator.patch
Patch0007:	0007-Fix-building-signed-kernels-on-setups-other-than-koj.patch
Patch0008:	0008-Add-D_GLIBCXX_ASSERTIONS-to-CPPFLAGS.patch
Patch0009:	0009-macros.pesign-handle-centos-like-rhel-with-rhelver.patch
Patch0010:	0010-Detect-the-presence-of-rpm-sign-when-checking-for-rh.patch
Patch0011:	0011-Rename-README-README.md.patch
Patch0012:	0012-README.md-show-off-a-bit-more.patch
Patch0013:	0013-Fix-missing-line-in-README.md.patch
Patch0014:	0014-Fix-typo-in-efikeygen-command.patch
Patch0015:	0015-pesigcheck-Fix-crash-on-digest-match.patch
Patch0016:	0016-cms-store-digest-as-pointer-instead-of-index.patch
Patch0017:	0017-Fix-mandoc-invocation-to-not-produce-garbage.patch
Patch0018:	0018-Work-around-GCC-being-obnoxiously-incompatible-with-.patch
Patch0019:	0019-get_password_passthrough-handle-the-callback-context.patch
Patch0020:	0020-read_password-only-prune-CR-NL-from-the-end-of-the-f.patch
Patch0021:	0021-Revert-cms-store-digest-as-pointer-instead-of-index.patch
Patch0022:	0022-CMS-add-some-minor-cleanups.patch
Patch0023:	0023-CMS-make-cms-selected_digest-an-index-again.patch

# Our own patches
Patch1000:	pesign-0.112-pass-linker-flags-correctly.patch
BuildRequires:	pkgconfig(efivar)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	gnu-efi
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(nss)
BuildRequires:	nss
BuildRequires:	pkgconfig(popt)
Requires:	nss
Requires:	popt
Requires:	rpm
Requires(pre):	shadow

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q -T -b 0
%setup -q -T -D -c -n pesign-%{version}/ -a 1
%autopatch -p1

%build
%make_build PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
mkdir -p %{buildroot}/%{_libdir}

make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install_systemd

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*

mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign/
mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/
cp -a etc/pki/pesign/* %{buildroot}%{_sysconfdir}/pki/pesign/
cp -a etc/pki/pesign-rh-test/* %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/

rm -vf %{buildroot}/usr/share/doc/pesign-%{version}/COPYING

# rpm5 is cute
mkdir -p %{buildroot}%{_sysconfdir}/rpm/macros.d
mv %{buildroot}%{_sysconfdir}/rpm/macros.pesign %{buildroot}%{_sysconfdir}/rpm/macros.d/pesign.macros

# No idea why they got this one wrong
sed -i -e 's,/var/run,/run,g' %{buildroot}%{_tmpfilesdir}/pesign.conf

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

%posttrans
certutil -d %{_sysconfdir}/pki/pesign/ -X -L > /dev/null

%files
%doc README.md TODO
%{_bindir}/authvar
%{_bindir}/efikeygen
%{_bindir}/pesigcheck
%{_bindir}/pesign
%{_bindir}/pesign-client
%{_bindir}/pesum
%dir %{_libexecdir}/pesign/
%dir %attr(0770,pesign,pesign) %{_sysconfdir}/pki/pesign/
%config(noreplace) %attr(0660,pesign,pesign) %{_sysconfdir}/pki/pesign/*
%dir %attr(0775,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/
%config(noreplace) %attr(0664,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/*
%{_libexecdir}/pesign/pesign-authorize
%{_libexecdir}/pesign/pesign-rpmbuild-helper
%config(noreplace)/%{_sysconfdir}/pesign/users
%config(noreplace)/%{_sysconfdir}/pesign/groups
%{_sysconfdir}/popt.d/pesign.popt
%{_sysconfdir}/rpm/macros.d/pesign.macros
%doc %{_mandir}/man*/*
%dir %attr(0770, pesign, pesign) %{_rundir}/%{name}
%ghost %attr(0660, -, -) %{_rundir}/%{name}/socket
%ghost %attr(0660, -, -) %{_rundir}/%{name}/pesign.pid
%{_tmpfilesdir}/pesign.conf
%{_unitdir}/pesign.service
