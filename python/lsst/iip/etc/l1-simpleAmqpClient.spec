%define lsstpath /opt/lsst

Name:           lsst-simpleAmqpClient		
Version:        2.4.0  	
Release:	1%{?dist}
Summary:        LSST Rabbitmq C++ Library 2.4.0	

Group:          Applications/System	
License:        MIT	
URL:            https://github.com/alanxz/SimpleAmqpClient	
Source0:        https://github.com/alanxz/SimpleAmqpClient/archive/v2.4.0.zip

BuildRequires:  cmake	
BuildRequires:  lsst-rabbitmq-c	
BuildRequires:  lsst-boost

%description
Rabbitmq C++ Library for use in Large Synoptic Survey Telescope Data
Management System

%prep
%setup -q -n SimpleAmqpClient-2.4.0
mkdir -p %{buildroot}/%{lsstpath}/bin
mkdir -p %{buildroot}/%{lsstpath}/lib
mkdir -p %{buildroot}/%{lsstpath}/include
mkdir -p %{buildroot}/%{lsstpath}/config
mkdir -p %{buildroot}/%{lsstpath}/share

%build
%cmake . -DCMAKE_INSTALL_PREFIX=%{lsstpath} -DBOOST_ROOT=%{lsstpath}
%make_build

%install
%make_install

%check
ctest -V %{?_smp_mflags}

%files
/opt/lsst/include/*
/opt/lsst/lib/*

%doc

%changelog

