%define lsstpath /opt/lsst

Name:           lsst-rabbitmq-c		
Version:        0.8.0  	
Release:	1%{?dist}
Summary:        LSST Rabbitmq C Library	0.8.0

Group:          Applications/System	
License:        MIT	
URL:            https://github.com/alanxz/rabbitmq-c	
Source0:        https://github.com/alanxz/rabbitmq-c/archive/v0.8.0.zip	

BuildRequires:  cmake	

%description
Rabbitmq C Library for usage in Large Synoptic Survey Telescope Data
Management System

%prep
%setup -q -n rabbitmq-c-0.8.0
mkdir -p %{buildroot}%{lsstpath}/bin
mkdir -p %{buildroot}%{lsstpath}/lib
mkdir -p %{buildroot}%{lsstpath}/include
mkdir -p %{buildroot}%{lsstpath}/config
mkdir -p %{buildroot}%{lsstpath}/share

%build
%cmake . -DCMAKE_INSTALL_PREFIX=%{lsstpath}
%make_build

%install
%make_install

%check
ctest -V %{?_smp_mflags}

%files
/opt/lsst/bin/*
/opt/lsst/include/*
/opt/lsst/lib64/*

%doc

%changelog

