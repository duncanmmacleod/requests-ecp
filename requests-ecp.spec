%define name requests-ecp
%define version 0.2.2
%define release 1

# -- metadata ---------------

BuildArch: noarch
Group:     Development/Libraries
License:   GPLv3+
Name:      %{name}
Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Prefix:    %{_prefix}
Release:   %{release}%{?dist}
Source0:   %pypi_source
Summary:   A SAML/ECP authentication handler for python-requests
Url:       https://github.com/duncanmmacleod/requests-ecp
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>
Version:   %{version}

# -- build requirements -----

BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: /usr/bin/python3
BuildRequires: python3-rpm-macros
BuildRequires: python%{python3_pkgversion}-lxml
BuildRequires: python%{python3_pkgversion}-pytest
BuildRequires: python%{python3_pkgversion}-requests
BuildRequires: python%{python3_pkgversion}-requests-kerberos
BuildRequires: python%{python3_pkgversion}-requests-mock
BuildRequires: python%{python3_pkgversion}-setuptools >= 30.3.0

# -- packages ---------------

# src.rpm
%description
requests-ecp adds optional SAML/ECP authentication support
for the Requests Python library.

%package -n python%{python3_pkgversion}-%{name}
Summary: %{summary}
Requires: python%{python3_pkgversion}-lxml
Requires: python%{python3_pkgversion}-requests
Requires: python%{python3_pkgversion}-requests-kerberos
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
requests-ecp adds optional SAML/ECP authentication support
for the Requests Python library.  This package provides
the Python %{python3_version} library.

# -- build ------------------

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
export PATH="%{buildroot}%{_bindir}:${PATH}"
%{__python3} -m pytest --verbose -ra --pyargs requests_ecp

%clean
rm -rf $RPM_BUILD_ROOT

# -- files ------------------

%files -n python%{python3_pkgversion}-%{name}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- changelog --------------

%changelog
* Fri Mar 19 2021 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.2-1
- update for 0.2.2
- tests are now bundled as part of the package
- add pytest run during rpmbuild check stage

* Mon Mar 23 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.1-1
- update for 0.2.1

* Mon Mar 09 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.0-1
- development release
- removed python2 support

* Mon Feb 17 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.1-1
- bug-fix release

* Fri Feb 7 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-1
- first release
