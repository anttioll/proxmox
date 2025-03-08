#!/usr/bin/bash
# Asettaa kaikkien opiskelijakäyttäjätunnusten salasanaksi Passw0rd!

for USERNUMBER in {1..20}; do
  pvesh set /access/password -userid kaouser$USERNUMBER@pve -password Passw0rd!
done
