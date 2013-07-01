Name:           sc3-program-repo
Version:        1.0
Release:        1%{?dist}
Summary:        SCE.COM Program repository for Enterprise Linux configuration

Group:          System Environment/Base

License:        GPLv3
URL:            http://vclx00927.sce.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%description
This package contains the SCE.COM Program repository for Enterprise Linux
GPG key as well as configuration for yum.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/
cp -p "sc3-program-repo-1.0/sc3.repo" $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/
cp -p "sc3-program-repo-1.0/sc3repopubkey.pub" $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
/etc/yum.repos.d/sc3.repo
/etc/pki/rpm-gpg/sc3repopubkey.pub

%changelog
* Thu Jun 13 2013 Johann Romero <johann.romero@gmail.com> - 1-0
- My RPM for installing repository file and GPG key
