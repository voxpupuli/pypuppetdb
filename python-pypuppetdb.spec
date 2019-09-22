%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-pypuppetdb
Version:        1.2.0
Release:        2%{?dist}
Summary:        A Python puppetdb API

Group:          Development/Languages
License:        Apache
URL:            https://github.com/nedap/pypuppetdb
Source0:        http://pypi.python.org/packages/source/p/pypuppetdb/pypuppetdb-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

BuildArch:      noarch
BuildRequires:  python-setuptools
Requires: python-requests >= 1.1.0
Requires: python >= 2.6

%description
pypuppetdb is a library to work with PuppetDB's REST API. It is implemented using the requests library.
This library is a thin wrapper around the REST API providing some convinience functions and objects to request and hold data from PuppetDB.
To use this library you will need: Python 2.6 or 2.7 or Python 3.3.

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
* Tue Oct 15 2013 Klavs Klavsen <Klavs@EnableIT.dk> - 0.0.4-2
- Add requirements, description and other small cleanups.
* Mon Oct 14 2013 Klavs Klavsen <Klavs@EnableIT.dk> - 0.0.4-1
- Initial release.

