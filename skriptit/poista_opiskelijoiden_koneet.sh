#!/usr/bin/bash
# Sammuttaa ja poistaa kaikki opiskelijoiden koneet 100 - 159 yksitellen
# ja poistaa niiden kiintolevyt

for VMID in 1{00..59}; do
  if [ $VMID -lt 130 ]; then
    NODE="proxmox1"
    REPL_NODE="proxmox2"
  else
    NODE="proxmox2"
    REPL_NODE="proxmox1"
  fi
  pvesh create /nodes/$NODE/qemu/$VMID/status/stop
  pvesh delete /nodes/$NODE/qemu/$VMID -destroy-unreferenced-disks 1 -purge 1
  for INDEX in {0..3}; do
    pvesh delete /nodes/$REPL_NODE/storage/vm/content/vm-$VMID-disk-$INDEX
  done
done
