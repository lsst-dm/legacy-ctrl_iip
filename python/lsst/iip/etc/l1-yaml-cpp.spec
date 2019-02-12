%define lsstpath /opt/lsst

Name:           lsst-yaml-cpp		
Version:        0.5.3  	
Release:	1%{?dist}
Summary:        LSST YAML C++ Library 0.5.3	

Group:          Applications/System	
License:        MIT	
URL:            https://github.com/jbeder/yaml-cpp	
Source0:        https://github.com/jbeder/yaml-cpp/archive/yaml-cpp-0.5.3.zip

BuildRequires:  cmake	
BuildRequires:  lsst-rabbitmq-c	
BuildRequires:  lsst-boost

%description
YAML C++ Library for use in Large Synoptic Survey Telescope Data
Management System

%prep
%setup -q -n yaml-cpp-yaml-cpp-0.5.3
mkdir -p %{buildroot}%{lsstpath}/bin
mkdir -p %{buildroot}%{lsstpath}/lib
mkdir -p %{buildroot}%{lsstpath}/include
mkdir -p %{buildroot}%{lsstpath}/config
mkdir -p %{buildroot}%{lsstpath}/share

%build
%cmake . -DCMAKE_INSTALL_PREFIX=%{lsstpath} -DBOOST_ROOT=%{lsstpath}
%make_build

%install
%make_install

%check
ctest -V %{?_smp_mflags}

%files
/opt/lsst/include/*
/opt/lsst/lib64/*

%doc

%changelog

