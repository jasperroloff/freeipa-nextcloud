%global debug_package %{nil}
%global plugin_name nextcloud

%global ipa_python3_sitelib %{python3_sitelib}

Name:           freeipa-%{plugin_name}
Version:        0.1.8
Release:        1%{?dist}
Summary:        nextcloud integration for FreeIPA

BuildArch:      noarch

License:        AGPLv3
URL:            https://github.com/jasperroloff/freeipa-nextcloud
Source0:        freeipa-nextcloud-%{version}.tar.gz


BuildRequires: ipa-server-common >= 4.6.0
BuildRequires: python3-devel
BuildRequires: python3-ipaserver >= 4.6.0

Requires(post): python3-ipa-%{plugin_name}-server
Requires: python3-ipa-%{plugin_name}-server

%description
A FreeIPA extension to manage nextcloud quotas

%package -n python3-ipa-%{plugin_name}-server
Summary: Server side of nextcloud plugin for FreeIPA
License: AGPLv3
Requires: python3-ipaserver

%description -n python3-ipa-%{plugin_name}-server
A FreeIPA extension to manage nextcloud quotas.
This package adds server-side support for FreeIPA.

%prep
%autosetup

%build
touch debugfiles.list

%install
rm -rf $RPM_BUILD_ROOT
%__mkdir_p %buildroot/%_datadir/ipa/schema.d
%__mkdir_p %buildroot/%_datadir/ipa/updates
%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}

targets="ipaserver"
for s in $targets ; do
    %__mkdir_p %buildroot/%{ipa_python3_sitelib}/$s/plugins
    for j in $(find plugin/$s/plugins -name '*.py') ; do
        %__cp $j %buildroot/%{ipa_python3_sitelib}/$s/plugins
    done
done

for j in $(find plugin/schema.d -name '*.ldif') ; do
    %__cp $j %buildroot/%_datadir/ipa/schema.d
done

#for j in $(find plugin/updates -name '*.update') ; do
#    %__cp $j %buildroot/%_datadir/ipa/updates
#done

for j in $(find plugin/ui -name '*.js') ; do
    %__cp $j %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}
done

%posttrans
ipa_interp=python3
$ipa_interp -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files
%license LICENSE
%_datadir/ipa/schema.d/*
#%_datadir/ipa/updates/*
%_datadir/ipa/ui/js/plugins/%{plugin_name}/*

%files -n python3-ipa-%{plugin_name}-server
%{ipa_python3_sitelib}/ipaserver/plugins/*

%changelog
* Fri Feb 23 2024 Jasper Roloff <jasperroloff@gmail.com> 0.1.8-1
- upgrade fedora to 36 (jasperroloff@gmail.com)

* Sun Jun 19 2022 Jasper Roloff <jasperroloff@gmail.com> 0.1.7-1
- upgrade github actions (jasperroloff@gmail.com)
- fix build (jasperroloff@gmail.com)
- upgrade to fedora 35 (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.6-1
- fix error with groups_mod callback (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.5-1
- fix import issue (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.4-1
- add group support (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.3-1
- merge both plugins into one single plugin (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.2-1
- fix error w/ unpackaged file (jasperroloff@gmail.com)

* Wed Aug 11 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.1-1
- new package built with tito

