Name:           jrbackup
Version:        1.0
Release:        1%{?dist}
Summary:        JR's backup script utility

Group:          System Environment/Base

License:        GPLv3
URL:            http://jrms02/myrepo/el/6/products/x86_64/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:      noarch

%description
This package contains the basic scripts to setup the jrbackup utility.

%prep
%setup -q -c -n %{name}-%{version}

%build

%install
basepath="/apps/"

mkdir -p $basepath
cp -r "jrbackup/" $basepath

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc

%changelog
* Tue Jul 02 2013 Johann Romero <johann.romero@gmail.com> - 1-0
- Initial deployment of basic jrbackup scripts
