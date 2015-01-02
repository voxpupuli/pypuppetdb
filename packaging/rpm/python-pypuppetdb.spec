%if 0%{?fedora} > 12
%global with_python3 1
%else
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

# use "--with tests" to run tests.
# tests not yet working in the rpm environment, so disabled by default
%bcond_with tests

%global srcname		pypuppetdb
%global srcname_init	%(c=%{srcname}; echo ${c:0:1})
%global srcversion	0.1.1

Name:           python-%{srcname}
Version:        0.1.1
Release:        1%{?dist}
Epoch:          1
Summary:        A python library for working with the PuppetDB REST API

Group:          Development/Libraries
License:        Apache License 2.0
URL:            https://github.com/puppet-community/pypuppetdb
Source0:        http://pypi.python.org/packages/source/%{srcname_init}/%{srcname}/%{srcname}-%{srcversion}.tar.gz

BuildArch:      noarch
Requires:       python-requests
BuildRequires:  python-setuptools
%if 0%{?with tests}
BuildRequires:  python-requests
BuildRequires:  pytest
BuildRequires:  python-mock
BuildRequires:  python-httpretty
BuildRequires:  python-pytest-pep8
BuildRequires:  python-coverage
%endif

%description
pypuppetdtb is a library to work with PuppetDB's REST API. It is implemented
using the requests library.

This library is a thin wrapper around the REST API providing some convinience
functions and objects to request and hold data from PuppetDB.

%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description doc
Documentation and examples for %{name}.

%if 0%{?with_python3}
%package -n python3-%{srcname}
Summary:        A python library for working with the PuppetDB REST API
BuildRequires:  python3-requests

%description -n python3-%{srcname}
pypuppetdtb is a library to work with PuppetDB's REST API. It is implemented
using the requests library.

This library is a thin wrapper around the REST API providing some convinience
functions and objects to request and hold data from PuppetDB.

%package -n python3-%{srcname}-doc
Summary:        Documentation for python3-%{srcname}
Group:          Documentation
Requires:       python3-%{srcname} = %{epoch}:%{version}-%{release}

%description -n python3-%{srcname}-doc
Documentation and examples for python3-%{srcname}.
%endif


%prep
%setup -q -n %{srcname}-%{srcversion}

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
find %{py3dir} -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
%endif


%build
%{__python} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif


%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# The docs are not included in the pypuppetdb tarballs that have been uploaded
# to pypi so we can't build them here
#make -C docs html

rm -rf %{buildroot}%{python_sitelib}/site.py
rm -rf %{buildroot}%{python_sitelib}/site.py[co]
rm -rf %{buildroot}%{python_sitelib}/easy-install.pth

# uncomment this when docs are being built
#rm -rf docs/_build/html/.buildinfo

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root %{buildroot}

# The docs are not included in the pypuppetdb tarballs that have been uploaded
# to pypi so we can't build them here
#make -C docs html

rm -rf %{buildroot}%{python3_sitelib}/site.py
rm -rf %{buildroot}%{python3_sitelib}/site.py[co]
rm -rf %{buildroot}%{python3_sitelib}/easy-install.pth
rm -rf %{buildroot}%{python3_sitelib}/__pycache__/site.cpython-3?.pyc

# uncomment this when docs are being built
#rm -rf docs/_build/html/.buildinfo
popd
%endif


%check
%if 0%{?with tests}
%{__python} setup.py test

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py test
popd
%endif
%endif


%files
%doc LICENSE PKG-INFO CHANGELOG.rst README.rst
%{python_sitelib}/*.egg-info
%{python_sitelib}/%{srcname}

%files doc
# uncomment this when docs are being built
#%doc docs/_build/html

%if 0%{?with_python3}
%files -n python3-%{srcname}
%doc LICENSE PKG-INFO CHANGELOG.rst README.rst
%{python3_sitelib}/*.egg-info
%{python3_sitelib}/%{srcname}

%files -n python3-%{srcname}-doc
# uncomment this when docs are being built
#%doc docs/_build/html
%endif


%changelog
* Fri Jan 02 2015 Robin Bowes <robin.bowes@yo61.com> - 1:0.1.1-1
- Initial packaging
