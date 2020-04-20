%define major 1
%define api 2.2
%define libname %mklibname %{name} %{api} %{major}
%define devname %mklibname %{name} -d

Summary:	GNU implementation of Scheme for application extensibility
Name:		guile
Version:	2.2.4
Release:	3
License:	LGPLv2+
Group:		Development/Other
Url:		http://www.gnu.org/software/guile/guile.html
Source0:	ftp://ftp.gnu.org/pub/gnu/guile/%{name}-%{version}.tar.xz
#Patch0:		guile-2.0.7-64bit-fixes.patch
Patch1:		guile-2.0.7-drop-ldflags-from-pkgconfig.patch
Patch3:		guile-2.0.7-turn-off-gc-test.patch
Patch4:		guile-2.0.3-mktemp.patch
#Patch5:		workaround-ice-ssa-corruption.patch

BuildRequires:	chrpath
BuildRequires:	libunistring-devel
BuildRequires:	texinfo
# for srfi-19.test
BuildRequires:	timezone
BuildRequires:	gettext-devel
BuildRequires:	gmp-devel
BuildRequires:	libtool-devel
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pkgconfig(bdw-gc)

%description
GUILE (GNU's Ubiquitous Intelligent Language for Extension) is a
library implementation of the Scheme programming language, written in
C. GUILE provides a machine-independent execution platform that can
be linked in as a library during the building of extensible programs.

Install the guile package if you'd like to add extensibility to
programs that you are developing. You'll also need to install the
guile-devel package.

%files
%doc AUTHORS GUILE-VERSION README THANKS
%{_bindir}/%{name}
%{_bindir}/%{name}-tools
%{_bindir}/guild
%{_libdir}/%{name}
%exclude %{_libdir}/%{name}/%{api}
%{_datadir}/%{name}
%exclude %{_datadir}/%{name}/%{api}
%{_mandir}/man1/guile.1.*
%{_infodir}/*

%triggerin -- slib
ln -sfT ../../slib %{_datadir}/guile/%{api}/slib

rm -f %{_datadir}/guile/%{mver}/slibcat
export SCHEME_LIBRARY_PATH=%{_datadir}/slib/

# Build SLIB catalog
for pre in \
    "(use-modules (ice-9 slib))" \
    "(load \"%{_datadir}/slib/guile.init\")"
do
    %{_bindir}/guile -c "$pre
        (set! implementation-vicinity (lambda () \"%{_datadir}/guile/%{api}/\"))
        (require 'new-catalog)" &> /dev/null && break
    rm -f %{_datadir}/guile/%{api}/slibcat
done
:

%triggerun -- slib
if [ "$1" = 0 -o "$2" = 0 ]; then
    rm -f %{_datadir}/guile/%{api}/slib{,cat}
fi

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Libraries for Guile %{version}
Group:		System/Libraries
Requires:	%{name}-runtime = %{EVRD}
Obsoletes:	%{mklibname guilereadline 18 18} < 2.2.3

%description -n %{libname}
This package contains Guile shared object libraries.

%files -n %{libname}
%{_libdir}/lib%{name}-%{api}.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Development headers and static library for libguile
Group:		Development/C
Requires:	%{name} >= %{EVRD}
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
# For -lgc, requested by pkg-config --libs guile-2.2
Requires:	pkgconfig(bdw-gc)
Requires:	gmp-devel

%description -n %{devname}
This package contains the development headers and the static library
for libguile. C headers, aclocal macros, the `guile1.4-snarf' and
`guile-config' utilities, and static `libguile' library for Guile, the
GNU Ubiquitous Intelligent Language for Extension

%files -n %{devname}
%{_bindir}/%{name}-config
%{_bindir}/%{name}-snarf
%{_datadir}/aclocal/*
%{_includedir}/%{name}
%{_libdir}/lib%{name}-%{api}.so
%{_libdir}/pkgconfig/%{name}*.pc
%{_datadir}/gdb/auto-load%{_libdir}/libguile*.scm

#----------------------------------------------------------------------------

%package runtime
Summary:	Guile runtime library
Group:		System/Libraries
Conflicts:	%{name} < 2.0.5-1

%description runtime
This package contains Scheme runtime for GUILE, including ice-9
Scheme module.

%files runtime
%{_libdir}/%{name}/%{api}/*
%{_datadir}/%{name}/%{api}/*.scm
%{_datadir}/%{name}/%{api}/*.txt
%{_datadir}/%{name}/%{api}/ice-9/*
%{_datadir}/%{name}/%{api}/language/*
%{_datadir}/%{name}/%{api}/oop/*
%{_datadir}/%{name}/%{api}/rnrs/*
%{_datadir}/%{name}/%{api}/scripts/*
%{_datadir}/%{name}/%{api}/srfi/*
%{_datadir}/%{name}/%{api}/sxml/*
%{_datadir}/%{name}/%{api}/system/*
%{_datadir}/%{name}/%{api}/texinfo/*
%{_datadir}/%{name}/%{api}/web/*
%ghost %{_datadir}/%{name}/%{api}/slibcat
%ghost %{_datadir}/%{name}/%{api}/slib

#----------------------------------------------------------------------------

%prep
%setup -q
%apply_patches
autoreconf -vfi

#fix encodings
for i in libguile/ChangeLog*; do
    mv $i $i.old
    iconv -f ISO8859-1 -t UTF-8 $i.old -o $i
done

%build
# http://llvm.org/bugs/show_bug.cgi?id=14406
export CC=gcc
export CXX=g++
%configure \
    --disable-error-on-warning \
    --disable-rpath \
    --with-threads \
    --with-pic

%make

%install
%makeinstall_std

#remove rpath
chrpath -d %{buildroot}%{_bindir}/%{name}

#for ghost files
touch %{buildroot}%{_datadir}/%{name}/%{api}/slibcat
touch %{buildroot}%{_datadir}/%{name}/%{api}/slib

mkdir -p %{buildroot}/%{_datadir}/gdb/auto-load%{_libdir}
mv -f %{buildroot}%{_libdir}/libguile-*gdb.scm %{buildroot}%{_datadir}/gdb/auto-load%{_libdir}

#slib needs this
mkdir -p %{buildroot}%{_datadir}/guile/site
