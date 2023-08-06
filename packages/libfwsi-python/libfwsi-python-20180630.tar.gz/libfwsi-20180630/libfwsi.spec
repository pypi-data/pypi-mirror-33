Name: libfwsi
Version: 20180630
Release: 1
Summary: Library to access the Windows Shell Item format
Group: System Environment/Libraries
License: LGPL
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libfwsi
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
          
          

%description
Library to access the Windows Shell Item format

%package devel
Summary: Header files and libraries for developing applications for libfwsi
Group: Development/Libraries
Requires: libfwsi = %{version}-%{release}

%description devel
Header files and libraries for developing applications for libfwsi.

%package python
Summary: Python 2 bindings for libfwsi
Group: System Environment/Libraries
Requires: libfwsi = %{version}-%{release} python
BuildRequires: python-devel

%description python
Python 2 bindings for libfwsi

%package python3
Summary: Python 3 bindings for libfwsi
Group: System Environment/Libraries
Requires: libfwsi = %{version}-%{release} python3
BuildRequires: python3-devel

%description python3
Python 3 bindings for libfwsi

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python2 --enable-python3
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%license COPYING
%doc AUTHORS README
%attr(755,root,root) %{_libdir}/*.so.*

%files devel
%defattr(644,root,root,755)
%license COPYING
%doc AUTHORS README ChangeLog
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/pkgconfig/libfwsi.pc
%{_includedir}/*
%{_mandir}/man3/*

%files python
%defattr(644,root,root,755)
%license COPYING
%doc AUTHORS README
%{_libdir}/python2*/site-packages/*.a
%{_libdir}/python2*/site-packages/*.la
%{_libdir}/python2*/site-packages/*.so

%files python3
%defattr(644,root,root,755)
%license COPYING
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.la
%{_libdir}/python3*/site-packages/*.so

%changelog
* Sat Jun 30 2018 Joachim Metz <joachim.metz@gmail.com> 20180630-1
- Auto-generated

