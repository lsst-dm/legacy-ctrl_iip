%define lsstpath /opt/lsst

Name:           lsst-boost	
Version:        1.63.0	
Release:	1%{?dist}
Summary:        LSST Boost 1.63.0	

Group:		Applications/Systems
License:        MIT	
URL:	        https://www.boost.org	
Source0:        https://sourceforge.net/projects/boost/files/boost/1.63.0/boost_1_63_0.tar.gz	

BuildRequires:  gcc	
BuildRequires:  python-devel

%description
Boost-1.63.0 libraries for use in Large Synoptic Survey Telescope

%prep
%setup -q -n boost_1_63_0
mkdir -p %{buildroot}%{lsstpath}/bin
mkdir -p %{buildroot}%{lsstpath}/lib
mkdir -p %{buildroot}%{lsstpath}/include
mkdir -p %{buildroot}%{lsstpath}/config
mkdir -p %{buildroot}%{lsstpath}/share

%build
/usr/bin/bash bootstrap.sh --prefix=%{buildroot}%{lsstpath}
./b2 link=shared

%install
./b2 install --prefix=%{buildroot}%{lsstpath}

%files
%defattr(-,root,root)
/opt/lsst/include/boost/*
/opt/lsst/lib/*

%doc

%changelog

