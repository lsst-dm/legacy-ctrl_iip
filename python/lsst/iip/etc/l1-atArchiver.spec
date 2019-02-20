%define lsstpath /opt/lsst/dm-prompt
%define gitbranch tickets/DM-17833
%define gitdash tickets-DM-17833
%define user ATS

Name:	        lsst-atArchiver	
Version:        1.6	
Release:	1%{?dist}
Summary:        ATArchiver software package for Data Management Services	

Group:	        Applications/System	
License:        MIT	
URL:		http://www.ncsa.illinois.edu/enabling/data/lsst
Source0:        https://github.com/lsst/ctrl_iip/archive/%{gitbranch}.zip	

BuildRequires:  python36 python36-devel	

BuildArch:      x86_64

%description
ATArchiver software manages the compute resources for Data Management Software
System to perform image processing.

%prep
%setup -q -n ctrl_iip-%{gitdash}

%install
cd python/lsst/iip

install -d %{buildroot}%{lsstpath}/bin %{buildroot}%{lsstpath}/bin/logs
install -d %{buildroot}/etc/systemd/system
install -m 755 -D *.py %{buildroot}%{lsstpath}/bin
install -m 755 -D L1SystemCfg.yaml %{buildroot}%{lsstpath}/bin
install -D start_up/l1d-* %{buildroot}/etc/systemd/system

%files
%defattr(755, %{user}, %{user}, 755) 
%{lsstpath}/bin/*
%attr(-, root, root) /etc/systemd/system/l1d-*

%doc

%changelog
