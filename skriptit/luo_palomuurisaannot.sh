#!/usr/bin/bash
# Asettaa kaikille opiskelijakoneille palomuurisäännöt käyttöön.
# Palomuurisäännöt häviävät, jos virtuaalikone poistetaan.

cd /etc/pve/firewall
for VMID in 1{00..59}; do
  cp vm-palomuuri.fw $VMID.fw
done
