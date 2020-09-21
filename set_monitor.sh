#!/bin/bash

ifconfig -a 
# ifconfig wlan0 up

#initing ...
echo "[*] Check ENV"
stat /usr/lib/arm-linux-gnueabihf/libisl.so.10
stat /usr/lib/arm-linux-gnueabihf/libmpfr.so.4
echo "[*] Check done"
echo "[+] Initing"
cd /home/pi/nexmon
source setup_env.sh
make 

cd /home/pi/nexmon/patches/bcm43455c0/7_45_189/nexmon_csi
make install-firmware

cd /home/pi/nexmon/utilities/nexutil
make && make install


MAC=`iwlist wlan0 scan | grep -C 5 "ASUS" | grep "Address" | awk '{print $5}'`
echo "[+] MAC Address:$MAC"
CHANNEL=`iwlist wlan0 scan | grep -C 5 "ASUS" | grep "Channel:" | cut -d ":" -f 2`
echo "[+] Channel :$CHANNEL"
BW=20
echo "[+] BW:$BW"
echo "[+] generate encrypt key "

cd /home/pi/nexmon/patches/bcm43455c0/7_45_189/nexmon_csi/utils/makecsiparams
chmod +x makecsiparams
ENCRYPT=`./makecsiparams -c $CHANNEL/$BW -C 1 -N 1 -m $MAC`
echo $ENCRYPT

echo "[+] Configure the extractor using nexutil and the generated parameters"
/usr/bin/nexutil -Iwlan0 -s500 -b -l34 -v$ENCRYPT

echo "[+] done"

echo "[+] Enable monitor mode"
/usr/bin/nexutil -Iwlan0 -m1

echo "[+] Check the mode"
/usr/bin/nexutil -m 



