Summary:	Nagios performance data analysis tool
Name:		nagios-pnp
Version:	0.6.7
Release:	0.2
License:	GPL v2
Group:		Applications/System
URL:		http://www.pnp4nagios.org/pnp/start
Source0:	http://downloads.sourceforge.net/pnp4nagios/pnp4nagios-%{version}.tar.gz
# Source0-md5:	d3da00c9df9123a28da0b9cd3f910c07
Source1:	%{name}.logrotate
Source2:	%{name}.init
BuildRequires:	perl-Time-HiRes
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	rrdtool
BuildRequires:	sed >= 4.0
Conflicts:	logrotate < 3.8.0
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios
Requires:	perl-Time-HiRes
Requires:	php(gd)
Requires:	rc-scripts
Requires:	rrdtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PNP is an addon to Nagios which analyzes performance data provided by
plugins and stores them automatically into RRD-databases.

%prep
%setup -q -n pnp4nagios-%{version}
#%{__sed} -i -e 's/^INSTALL_OPTS="-o $nagios_user -g $nagios_grp"/INSTALL_OPTS=""/' configure

%build
%configure \
	--bindir=%{_sbindir} \
	--libexecdir=%{_libdir}/pnp \
	--sysconfdir=%{_sysconfdir}/pnp \
	--localstatedir=%{_localstatedir}/log/pnp \
	--datadir=%{_datadir}/nagios/pnp \
	--datarootdir=%{_datadir}/nagios/pnp \
	--with-perfdata-dir=%{_localstatedir}/lib/pnp \
	--with-perfdata-spool-dir=%{_localstatedir}/spool/pnp \
	--with-layout=default \
	--with-nagios-user=nagios \
	--with-nagios-group=nagios \
	--with-rrdtool=/usr/bin/rrdtool \
	--with-perfdata-logfile=/var/log/pnp \
	--with-httpd-conf=/etc/webapps/pnp \
	--with-base-url=/pnp \
	--with-init-dir=/etc/rc.d/init.d \

#  --without-kohana does not install the kohana framework
#  --with-kohana_system=<existing kohana system dir> Points to an already installed kohana framework



%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/webapps/pnp
%{__make} fullinstall \
	INSTALL_OPTS= \
	INIT_OPTS= \
	STRIP=: \
	DESTDIR=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT%{_sysconfdir}/pnp -name *-sample -exec rename '-sample' '' {} ';'
sed -i \
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
%doc AUTHORS ChangeLog COPYING INSTALL README THANKS
%dir %{_sysconfdir}/pnp
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pnp/*
%attr(754,root,root) /etc/rc.d/init.d/npcd
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/pnp
%attr(755,root,root) %{_sbindir}/npcd
%dir %{_libdir}/pnp
%attr(755,root,root) %{_libdir}/pnp/check_pnp_rrds.pl
%attr(755,root,root) %{_libdir}/pnp/process_perfdata.pl
%attr(755,root,root) %{_libdir}/pnp/rrd_convert.pl
%attr(755,root,root) %{_libdir}/pnp/verify_pnp_config.pl
%attr(755,nagios,nagios) %{_localstatedir}/lib/pnp
%attr(755,nagios,nagios) %{_localstatedir}/log/pnp
%attr(755,nagios,nagios) %{_localstatedir}/spool/pnp
%{_datadir}/nagios/pnp

%{_sysconfdir}/webapps/pnp/pnp4nagios.conf
# TODO: use system pkg
%{_libdir}/kohana
