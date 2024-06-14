%define srcname requests-ecp
%global distname %{lua:name = string.gsub(rpm.expand("%{srcname}"), "[.-]", "_"); print(name)}
%define version 0.3.2
%define release 1

# -- metadata ---------------

BuildArch: noarch
Group:     Development/Libraries
License:   GPLv3+
Name:      python-%{srcname}
Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Prefix:    %{_prefix}
Release:   %{release}%{?dist}
Source0:   %pypi_source %distname
Summary:   A SAML/ECP authentication handler for python-requests
Url:       https://git.ligo.org/computing/software/requests-ecp
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>
Version:   %{version}

# -- build requirements -----

# build
BuildRequires: python3-devel
BuildRequires: python3dist(lxml)
BuildRequires: python3dist(pip)
BuildRequires: python3dist(requests)
BuildRequires: python3dist(requests-gssapi) >= 1.2.2
BuildRequires: python3dist(setuptools) >= 30.3.0
BuildRequires: python3dist(wheel)

# testing
BuildRequires: python3dist(pytest)
BuildRequires: python3dist(requests-mock)

# -- packages ---------------

# src.rpm
%description
requests-ecp adds optional SAML/ECP authentication support
for the Requests Python library.

%package -n python3-%{srcname}
Summary: %{summary}
%description -n python3-%{srcname}
requests-ecp adds optional SAML/ECP authentication support
for the Requests Python library.  This package provides
the Python %{python3_version} library.
%files -n python3-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- build ------------------

%prep
%autosetup -n %{distname}-%{version}
# for RHEL < 9 hack together setup.{cfg,py} for old setuptools
%if 0%{?rhel} > 0 || 0%{?rhel} < 9
cat > setup.cfg << SETUP_CFG
[metadata]
name = %{srcname}
version = %{version}
author-email = %{packager}
description = %{summary}
license = %{license}
license_files = LICENSE
url = %{url}
[options]
packages = find:
python_requires = >=3.6
install_requires =
	lxml
	requests
SETUP_CFG
%endif
%if %{undefined pyproject_wheel}
cat > setup.py << SETUP_PY
from setuptools import setup
setup()
SETUP_PY
%endif

%build
%if %{defined pyproject_wheel}
%pyproject_wheel
%else
%py3_build_wheel
%endif

%install
%if %{defined pyproject_install}
%pyproject_install
%else
%py3_install_wheel %{distname}-%{version}-*.whl
%endif

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
%python3 -m pip show %{srcname} -f
%pytest --verbose -ra --pyargs requests_ecp

# -- changelog --------------

%changelog
* Mon Apr 29 2024 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.2-1
- update for 0.3.2
- update Python macros for RHEL>=8
- add legacy shims to pull metadata out of pyproject.toml
- rename source rpm to python-requests-ecp

* Mon Jul 17 2023 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.1-1
- update for 0.3.1

* Wed Oct 26 2022 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.0-1
- update for 0.3.0

* Mon Nov 22 2021 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.3-1
- update for 0.2.3
- use python3-gssapi as the kerberos backend

* Tue Mar 30 2021 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.2-2
- don't run tests on el7

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
