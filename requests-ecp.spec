%define name requests-ecp
%define version 0.2.1
%define release 1

# -- metadata ---------------

BuildArch: noarch
Group:     Development/Libraries
License:   GPL-3.0-or-later
Name:      %{name}
Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Prefix:    %{_prefix}
Release:   %{release}%{?dist}
Source0:   %pypi_source
Summary:   A SAML/ECP authentication handler for python-requests.
Url:       https://github.com/duncanmmacleod/requests-ecp
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>
Version:   %{version}

# -- build requirements -----

BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: /usr/bin/python3
BuildRequires: python3-rpm-macros
BuildRequires: python%{python3_pkgversion}-setuptools

# -- packages ---------------

# src.rpm
%description
The Python client for SAML ECP authentication.

%package -n python%{python3_pkgversion}-%{name}
Summary: %{summary}
Requires: python%{python3_pkgversion}-lxml
Requires: python%{python3_pkgversion}-requests
Requires: python%{python3_pkgversion}-requests-kerberos
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
The Python %{python3_version} %{name} library.

# -- build ------------------

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

# -- files ------------------

%files -n python%{python3_pkgversion}-%{name}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- changelog --------------

%changelog
* Mon Mar 23 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.1-1
- update for 0.2.1

* Mon Mar 09 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.0-1
- development release
- removed python2 support

* Mon Feb 17 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.1-1
- bug-fix release

* Fri Feb 7 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-1
- first release
