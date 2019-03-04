#!/usr/bin/env bash
# disable DPMS (Energy Star) features.
xset -dpms
# disable screen saver
xset s off
# don't blank the video device
xset s noblank
# disable mouse pointer
unclutter &
# run window manager
matchbox-window-manager -use_cursor no -use_titlebar no  &
# run browser
SCREEN_TOKEN=`md5sum /etc/machine-id | awk '{print $1;}'`
url='http://affichage-test.bde-insa-lyon.fr/display/'${SCREEN_TOKEN}
chromium-browser --noerrdialogs --disable-session-crashed-bubble --disable-infobars --disk-cache-size=180000000 --kiosk --no-first-run ${url}
echo "Chrome crash, reboot dans 120 sec, pour laisser le temps de se co en ssh si bootloop"
sleep 120
sudo reboot