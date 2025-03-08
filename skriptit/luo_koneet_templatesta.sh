#!/usr/bin/bash
# Luo opiskelijoiden koneet 100 - 159 mallipohjasta.
# TODO: VLAN-tunnisteet

#VMID=100
#USERS=( 1 11 )

#for USERNUMBER in {1..20}; do
#for USERNUMBER in "${USERS[@]}"; do
#  for VMNUMBER in {1..3}; do
#    if [ $USERNUMBER -lt 11 ]; then
#      pvesh create /nodes/proxmox1/qemu/10001/clone \
#        -newid $VMID \
#        -full 1 \
#        -name kaouser$USERNUMBER-vm$VMNUMBER
#    else
#      pvesh create /nodes/proxmox2/qemu/10002/clone \
#        -newid $VMID \
#        -full 1 \
#        -name kaouser$USERNUMBER-vm$VMNUMBER
#    fi
#    VMID=$[$VMID+1]
#  done
#done
