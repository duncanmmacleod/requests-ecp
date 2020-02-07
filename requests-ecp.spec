%define name requests-ecp
%define version 0.1.0
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

%if 0%{?rhel} && 0%{?rhel} <= 7

# python2 build (centos<=7 only)
BuildRequires: /usr/bin/python2
BuildRequires: python2-rpm-macros
BuildRequires: python-setuptools

%else

# python3 build (centos>=8 only)
BuildRequires: /usr/bin/python3
BuildRequires: python3-rpm-macros
BuildRequires: python%{python3_pkgversion}-setuptools

%endif

# -- packages ---------------

# src.rpm
%description
The Python client for SAML ECP authentication.

%if 0%{?rhel} && 0%{?rhel} <= 7

%package -n python2-%{name}
Summary: %{summary}
Requires: python-lxml
Requires: python-requests
Requires: python-requests-kerberos
%{?python_provide:%python_provide python2-%{name}}
%description -n python2-%{name}
The Python %{python2_version} %{name} library.

%else

%package -n python%{python3_pkgversion}-%{name}
Summary: %{summary}
Requires: python%{python3_pkgversion}-lxml
Requires: python%{python3_pkgversion}-requests
Requires: python%{python3_pkgversion}-requests-kerberos
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
%description -n python%{python3_pkgversion}-%{name}
The Python %{python3_version} %{name} library.

%endif

# -- build ------------------

%prep
%autosetup -n %{name}-%{version}

%build
%if 0%{?rhel} && 0%{?rhel} <= 7
# old setuptools does not support environment markers:
sed -i "/ ; /s/ ;.*/\",/g" setup.py
# build python2
%py2_build
%else
# build python3
%py3_build
%endif

%install
%if 0%{?rhel} && 0%{?rhel} <= 7
%py2_install
%else
%py3_install
%endif

%clean
rm -rf $RPM_BUILD_ROOT

# -- files ------------------

%if 0%{?rhel} && 0%{?rhel} <= 7

%files -n python2-%{name}
%license LICENSE
%doc README.md
%{python2_sitelib}/*

%else

%files -n python%{python3_pkgversion}-%{name}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%endif

# -- changelog --------------

%changelog
* Fri Feb 7 2020 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-1
- first release
