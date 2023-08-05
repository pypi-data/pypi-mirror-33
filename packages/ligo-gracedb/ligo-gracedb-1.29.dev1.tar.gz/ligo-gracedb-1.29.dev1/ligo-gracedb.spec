%define name              ligo-gracedb
%define version           1.29-0.1
%define unmangled_version 1.29-0.1
%define release           1

Summary:   Gravity Wave Candidate Event Database
Name:      %{name}
Version:   %{version}
Release:   %{release}%{?dist}
Source0:   %{name}-%{unmangled_version}.tar.gz
License:   GPL
Group:     Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:    %{_prefix}
Vendor:    Tanner Prestegard <tanner.prestegard@ligo.org>, Alexander Pace <alexander.pace@ligo.org>
Url:       http://www.lsc-group.phys.uwm.edu/daswg/gracedb.html

BuildArch: noarch
BuildRequires: rpm-build
BuildRequires: epel-rpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros
BuildRequires: python-setuptools
BuildRequires: python%{python3_pkgversion}-setuptools

%description
The gravitational-wave candidate event database (GraceDB) is a prototype 
system to organize candidate events from gravitational-wave searches and 
to provide an environment to record information about follow-ups. A simple 
client tool is provided to submit a candidate event to the database.

# -- python2-ligo-gracedb

%package -n python2-%{name}
Summary:  %{summary}
Provides: %{name}
Obsoletes: %{name} < 1.27-2
Conflicts: %{name}
Requires: python-six
Requires: python2-ligo-common

%{?python_provide:%python_provide python2-%{name}}

%description -n python2-%{name}
The gravitational-wave candidate event database (GraceDB) is a prototype 
system to organize candidate events from gravitational-wave searches and 
to provide an environment to record information about follow-ups. A simple 
client tool is provided to submit a candidate event to the database.

# -- python-3X-ligo-gracedb

%package -n python%{python3_pkgversion}-%{name}
Summary:  %{summary}
Requires: python%{python3_pkgversion}-six
Requires: python%{python3_pkgversion}-ligo-common

%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}

%description -n python%{python3_pkgversion}-%{name}
The gravitational-wave candidate event database (GraceDB) is a prototype 
system to organize candidate events from gravitational-wave searches and 
to provide an environment to record information about follow-ups. A simple 
client tool is provided to submit a candidate event to the database.

# -- build steps

%prep
%setup -n %{name}-%{unmangled_version}

%build
# build python3 first
%py3_build
# so that the scripts come from python2
%py2_build

%install
%py2_install
%py3_install

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python2-%{name}
%{_bindir}/gracedb
%{python2_sitelib}/*
%exclude %{python_sitelib}/ligo/gracedb/*pyo

%files -n python%{python3_pkgversion}-%{name}
%{python3_sitelib}/*
%exclude %{python3_sitelib}/ligo/gracedb/test/*pyo
