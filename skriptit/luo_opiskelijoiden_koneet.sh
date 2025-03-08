#!/usr/bin/bash
# Skripti luo tyhjät virtuaalikoneet 100 - 159.
# Jokainen käyttäjä saa kolme konetta nimeltä:
#   kaouser1-vm1, kaouser1-vm2, kaouser1-vm3
#   ...
#   kaouser20-vm1, kaouser20-vm2, kaouser20-vm3
# Käyttäjien 1 - 10 koneet menevät proxmox1-solmulle ja käyttäjien 11 - 20 koneet proxmox2-solmulle.
# Koneissa on verkkokortit net0 ja net1, joista net0 ei ole VLAN-merkitty.
# Verkkokortti net1 saa VLAN-tunnisteen koneiden välistä paikallista liikennettä varten.
# Käyttäjälle 1 VLAN-tunniste 1001, käyttäjälle 2 tunniste 1002 jne.

VMID=100
VLANTAG=1001

for USERNUMBER in {1..20}; do
  for VMNUMBER in {1..3}; do
    if [ $USERNUMBER -lt 11 ]; then
      NODE="proxmox1"
    else
      NODE="proxmox2"
    fi
    pvesh create /nodes/$NODE/qemu \
      -vmid $VMID \
      -agent 1 \
      -bios ovmf \
      -boot order=ide0\;ide1\;scsi0\;sata0\;net0 \
      -cores 4 \
      -cpu cputype=host \
      -efidisk0 vm:1,efitype=4m,pre-enrolled-keys=1,size=1M \
      -ide0 file=none,media=cdrom \
      -ide1 file=none,media=cdrom \
      -machine pc-q35-9.0 \
      -memory 6144 \
      -name kaouser$USERNUMBER-vm$VMNUMBER \
      -net0 virtio,bridge=vmbr0,firewall=1 \
      -net1 virtio,bridge=vmbr0,tag=$VLANTAG,firewall=0 \
      -numa 0 \
      -ostype win11 \
      -sata0 vm:100,discard=on,cache=writeback,size=100G \
      -scsi0 vm:100,discard=on,cache=writeback,size=100G \
      -scsihw virtio-scsi-pci \
      -tpmstate0 vm:1,size=4M,version=v2.0
    VMID=$[$VMID+1]
    VLANTAG=$[$VLANTAG+1]
  done
done
