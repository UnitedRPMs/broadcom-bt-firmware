%define debug_package %{nil}
%global _firmwarepath	/usr/lib/firmware

#globals for broadcom-bt-firmware
%global gitdate 20180921
%global commit0 c0bd928b8ae5754b6077c99afe6ef5c949a58f32 
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

Summary:	Firmware of Broadcom WIDCOMM® Bluetooth devices
Name:		broadcom-bt-firmware
Version:	12.0.1.1012
Release:	4%{?gver}%{?dist}
Source0:	https://github.com/winterheart/broadcom-bt-firmware/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Patch:		42c635dbd99fc1f65596b3dd0418a8bc78e7ee31.patch
Requires:	usbutils
Requires:	bluez
Requires:	pulseaudio-module-bluetooth
Recommends:	pavucontrol 
Recommends:	bluez-hid2hci

License:	Proprietary, only for exclusive uses of BROADCOM products and MIT
Group:		System/Kernel and hardware
URL:		https://github.com/winterheart/broadcom-bt-firmware

%description
This package provides the firmware of Broadcom WIDCOMM® Bluetooth 
devices (including BCM20702, BCM20703, BCM43142 chipsets and other) 
for Linux kernel. Since February 2017, Broadcom ships their drivers directly 
to Windows Update service. 

%prep
%autosetup -n %{name}-%{commit0} -p1

%build

# Nothing

%install
mkdir -p $RPM_BUILD_ROOT/%{_firmwarepath}
mkdir -p $RPM_BUILD_ROOT/etc/bluetooth/
cp -rf brcm/ $RPM_BUILD_ROOT/%{_firmwarepath}/
install -D LICENSE.broadcom_bcm20702 $RPM_BUILD_ROOT/%{_datadir}/licenses/%{name}/LICENSE

# You can use your computer's speakers as a bluetooth headset
echo '[General]
Enable=Source,Sink,Media,Socket' > $RPM_BUILD_ROOT/etc/bluetooth/audio.conf

# Why the latest kernel in Fedora requires a BCM.hcd?
touch $RPM_BUILD_ROOT/%{_firmwarepath}/brcm/BCM.hcd


%post
# Repeat, Why the latest kernel in Fedora requires a BCM.hcd?
set -x

# First, we need to delete obsoletes BCM's
modprobe -r btusb

# Start the magic
tmp=$(mktemp -d)

trap cleanup EXIT
cleanup() {
    set +e
    [ -z "$tmp" -o ! -d "$tmp" ] || rm -rf "$tmp"
}

pushd ${tmp}

A=$(lsusb | grep -i 'ID' | awk -F 'ID ' '{print $2}' | sed 's/:/-/g' | awk '{print $1}' > listID )
B=$( ls -1 /lib/firmware/brcm/ > installedID )

file=listID
while IFS= read -r line; do
        # display $line or do something with $line
if [ $( cat installedID | grep -c -i "$line" ) -gt 0 ]; then
    cp -f /lib/firmware/brcm/BCM*-$line.hcd /lib/firmware/brcm/BCM.hcd  
fi
done <"$file"
popd

modprobe btusb
hciconfig hci0 up
dmesg | grep -i 'blu'

%postun 
if [ -f %{_firmwarepath}/brcm/BCM.hcd ]; then
rm -f /lib/firmware/brcm/BCM.hcd
fi

%clean
rm -rf %{buildroot}

%files 
%{_datadir}/licenses/%{name}/LICENSE
%{_firmwarepath}/brcm/*.hcd
%ghost %{_firmwarepath}/brcm/BCM.hcd
%config %{_sysconfdir}/bluetooth/audio.conf

%changelog

* Fri Sep 21 2018 - David Va <davidva AT tuta DOT io> 12.0.1.1012-4.gitc0bd928
- added BCM43142A0-14e4-4365 firmware

* Thu Jul 26 2018 - David Va <davidva AT tuta DOT io> 12.0.1.1012-3.gitc0bd928
- Editable config Audio (A2DP sink)

* Fri May 04 2018 - David Vasquez <davidva AT tutanota DOT com> 12.0.1.1012-2.gitc0bd928
- BCM fix

* Wed Mar 21 2018 - David Vasquez <davidva AT tutanota DOT com> 12.0.1.1012-1.gitc0bd928
- Updated to 12.0.1.1012-1.gitc0bd928

* Fri Apr 14 2017 - David Vasquez <davidva AT tutanota DOT com> 12.0.1.1011-1
- Initial build
