%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-pypuppetdb
Version:        0.0.4
Release:        1%{?dist}
Summary:        A Python puppetdb API

Group:          Development/Languages
License:        Apache
URL:            https://github.com/nedap/pypuppetdb
Source0:        pypuppetdb-0.0.4.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

BuildArch:      noarch
BuildRequires:  python-setuptools

%description

%prep
%setup -q -n pypuppetdb-%{version}
%{__rm} -rf *.egg-info
%{__sed} -i 's,^#!.*env python.*$,#!/usr/bin/python,' setup.py

%build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --root %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc
%{python_sitelib}/*

%changelog
* Thu Oct 14 2013 Klavs Klavsen <Klavs@EnableIT.dk> - 0.0.4-1
- Initial release.

