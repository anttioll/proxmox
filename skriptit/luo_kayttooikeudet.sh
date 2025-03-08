#!/usr/bin/bash
# Asettaa opiskelijatunnuksille käyttöoikeudet vain omiin virtuaalikoneisiinsa
# ja ottaa ensin varmuuskopion olemassaolevista käyttöoikeuksista tiedostoon 'user.cfg.bak_päivämäärä'.
# Toimivat ja testatut käyttöoikeudet löytyvät tiedostosta '/etc/pve/user.cfg.defaults'.
# Kun virtuaalikone tuhotaan, tuhoaa se myös käyttöoikeudet, siksi ne pitää skriptistä uusiksi ajaa.

DATE=$(date +%Y_%m_%d_%H%M)

cd /etc/pve
cp user.cfg user.cfg.bak_$DATE
cp user.cfg.defaults user.cfg
