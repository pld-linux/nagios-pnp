# TODO
# warning: Installed (but unpackaged) file(s) found:
#   /usr/lib/pnp/check_pnp_rrds.pl
Summary:	Nagios performance data analysis tool
Name:		nagios-pnp
Version:	0.4.12
Release:	0.1
License:	GPL v2
Group:		Applications/System
URL:		http://www.pnp4nagios.org/pnp/start
Source0:	http://dl.sourceforge.net/pnp4nagios/pnp-%{version}.tar.gz
# Source0-md5:	eb833a4769a5b58aad0ac53cae3e3e9f
Source1:	%{name}.logrotate
Source2:	%{name}.init
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	rrdtool
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios
Requires:	php(gd)
Requires:	rc-scripts
Requires:	rrdtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PNP is an addon to Nagios which analyzes performance data provided by
plugins and stores them automatically into RRD-databases.

%prep
%setup -q -n pnp-%{version}
%{__sed} -i -e 's/^INSTALL_OPTS="-o $nagios_user -g $nagios_grp"/INSTALL_OPTS=""/' configure

%build
%configure \
	--bindir=%{_sbindir} \
	--libexecdir=%{_libexecdir}/pnp \
	--sysconfdir=%{_sysconfdir}/pnp \
	--localstatedir=%{_localstatedir}/log/pnp \
	--datadir=%{_datadir}/nagios/html/pnp \
	--datarootdir=%{_datadir}/nagios/html/pnp \
	--with-perfdata-dir=%{_localstatedir}/lib/pnp \
	--with-perfdata-spool-dir=%{_localstatedir}/spool/pnp

%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} install-config \
	DESTDIR=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT%{_sysconfdir}/pnp -name *-sample -exec rename "-sample" "" {} ';'
sed -i -e 's|/usr/libexec/process_perfdata.pl|/usr/libexec/pnp/process_perfdata.pl|' \
       -e 's|^log_type = syslog|log_type = file|' \
       $RPM_BUILD_ROOT%{_sysconfdir}/pnp/npcd.cfg

install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/pnp
install -d $RPM_BUILD_ROOT%{_localstatedir}/spool/pnp
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/pnp
install -Dp %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/pnp
install -Dp %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/npcd

# pnpsender is not built so no need to keep the man page
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/pnpsender.1

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add npcd
%service npcd restart

%preun
if [ "$1" = 0 ]; then
	%service npcd stop
	/sbin/chkconfig --del npcd
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS BUGS ChangeLog COPYING INSTALL NEWS README
%doc README.npcd THANKS TODO
%dir %{_sysconfdir}/pnp
%config(noreplace) %{_sysconfdir}/pnp/*
%config(noreplace) /etc/logrotate.d/pnp
%attr(755,root,root) %{_initrddir}/npcd
%attr(755,root,root) %{_sbindir}/npcd
%attr(755,root,root) %{_libexecdir}/pnp/process_perfdata.pl
%attr(755,nagios,nagios) %{_localstatedir}/lib/pnp
%attr(755,nagios,nagios) %{_localstatedir}/log/pnp
%attr(755,nagios,nagios) %{_localstatedir}/spool/pnp
%{_datadir}/nagios/html/pnp
