#!/usr/bin/bash

DATE=$(date +%Y_%m_%d)
TARGET_DIR=
HOST=""

# Ei poista vanhoja tar-palloja; jos proxmox1-solmun skripti ei pyöri, näitä alkaa kertyä
tar cfzP - /root | ssh root@$HOST "cat > $TARGET_DIR/root-$DATE-proxmox2.tar.gz"
tar cfzP - /etc/pve | ssh root@$HOST "cat > $TARGET_DIR/etc_pve-$DATE-proxmox2.tar.gz"
tar cfzP - /var/lib/pve-cluster | ssh root@$HOST "cat > $TARGET_DIR/var_lib_pve-cluster-$DATE-proxmox2.tar.gz"

if zfs snapshot -r rpool@proxmox2-$DATE && \
   zfs send -R rpool@proxmox2-$DATE | ssh root@$HOST "cat > $TARGET_DIR/rpool-$DATE-proxmox2.zfs";
then
	# Poistetaan vanhat snapshotit
	zfs list -t snapshot -o name | grep rpool@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
	zfs list -t snapshot -o name | grep rpool/ROOT@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
	zfs list -t snapshot -o name | grep rpool/ROOT/pve-1 | tac | tail -n +26 | xargs -n 1 zfs destroy -r
	zfs list -t snapshot -o name | grep rpool/data@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
	zfs list -t snapshot -o name | grep rpool/data/ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
	zfs list -t snapshot -o name | grep rpool/var-lib | tac | tail -n +26 | xargs -n 1 zfs destroy -r
fi
