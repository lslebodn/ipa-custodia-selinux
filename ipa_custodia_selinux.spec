# defining macros needed by SELinux
%global selinuxtype targeted
%if 0%{?fedora}
%global selinux_policyver 3.13.1-225
%else
%global selinux_policyver 3.13.1-144
%endif
%global moduletype contrib
%global modulename ipa_custodia

Name: ipa-custodia-selinux
Version: 0.1.1
Release: 1%{?dist}
License: GPLv3
URL: https://github.com/latchset/ipa-custodia-selinux
Summary: SELinux policies for FreeIPA's ipa-custodia
Source0: https://github.com/latchset/ipa-custodia-selinux/archive/v0.1.1.tar.gz
BuildArch: noarch
Requires: selinux-policy >= %{selinux_policyver}
%if 0%{?fedora}
Requires: freeipa-server >= 4.5.0
%else
Requires: ipa-server >= 4.5.0
%endif
BuildRequires: git
BuildRequires: pkgconfig(systemd)
BuildRequires: selinux-policy
BuildRequires: selinux-policy-devel
BuildRequires: bzip2
Requires(post): selinux-policy-base >= %{selinux_policyver}
Requires(post): libselinux-utils
Requires(post): policycoreutils

%if 0%{?fedora}
Requires(post): policycoreutils-python-utils
%else

Requires(post): policycoreutils-python
%endif

%description
SELinux policy modules for FreeIPA's ipa-custodia

%prep
%setup -q

%build
make

%pre
%selinux_relabel_pre -s %{selinuxtype}

%install
# install policy modules
install -d %{buildroot}%{_datadir}/selinux/packages
install -d -p %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -p -m 644 %{modulename}.if %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -m 0644 %{modulename}.pp.bz2 %{buildroot}%{_datadir}/selinux/packages
install -d %{buildroot}%{_libexecdir}/ipa

%check

%post
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/%{modulename}.pp.bz2
# Fixing the file context on /usr/libexec/ipa/ipa-custodia
/sbin/restorecon -F -v /usr/libexec/ipa/ipa-custodia
# Fixing the file context on /etc/ipa/custodia
if [ -d /etc/ipa/custodia ]; then
    /sbin/restorecon -F -R -v /etc/ipa/custodia
fi
# Fixing the file context on /var/log/ipa-custodia.audit.log
if [ -f /var/log/ipa-custodia.audit.log ]; then
    /sbin/restorecon -F -v /var/log/ipa-custodia.audit.log
fi

%postun
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s %{selinuxtype} %{modulename}
fi

%posttrans
%selinux_relabel_post -s %{selinuxtype}

%files
%defattr(-,root,root,0755)
%attr(0644,root,root) %{_datadir}/selinux/packages/%{modulename}.pp.bz2
%attr(0644,root,root) %{_datadir}/selinux/devel/include/%{moduletype}/%{modulename}.if

%changelog
* Mon Nov 06 2017 Christian Heimes <cheimes@redhat.com> - 0.1.1-1
- Use DAC_OVERRIDE instead of changing Dogtag's file permissions

* Mon Apr 24 2017 Christian Heimes <cheimes@redhat.com> - 0.1.0-1
- First Build
