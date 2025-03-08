#!/usr/bin/bash
# Säilyttää varmuuskopioita puoli vuotta

DATE=$(date +%Y_%m_%d)
TARGET_DIR=

# Luodaan tar-pallot hakemistoista /root, /etc/pve ja /var/lib/pve-cluster
if tar cfzP $TARGET_DIR/root_$DATE-proxmox1.tar.gz /root && \
   tar cfzP $TARGET_DIR/etc_pve_$DATE-proxmox1.tar.gz /etc/pve && \
   tar cfzP $TARGET_DIR/var_lib_pve-cluster_$DATE-proxmox1.tar.gz /var/lib/pve-cluster;
then
  # Poistetaan vanhat tar-pallot, jos edelliset komennot onnistuivat
  cd $TARGET_DIR
  ls | grep root_ | grep proxmox1 | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep root_ | grep proxmox2 | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep etc_pve_ | grep proxmox1 | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep etc_pve_ | grep proxmox2 | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep var_lib_ | grep proxmox1 | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep var_lib_ | grep proxmox2 | tac | tail -n +26 | xargs -n 1 rm -f
fi

# Luodaan snapshotit
if zfs snapshot -r rpool@proxmox1-$DATE && \
   zfs send -R rpool@proxmox1-$DATE > $TARGET_DIR/rpool-$DATE-proxmox1.zfs;
then
  # Poistetaan vanhat snapshotit, jos edelliset komennot onnistuivat
  cd $TARGET_DIR
  ls | grep proxmox1.zfs | tac | tail -n +26 | xargs -n 1 rm -f
  ls | grep proxmox2.zfs | tac | tail -n +26 | xargs -n 1 rm -f
  zfs list -t snapshot -o name | grep rpool@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
  zfs list -t snapshot -o name | grep rpool/ROOT@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
  zfs list -t snapshot -o name | grep rpool/ROOT/pve-1 | tac | tail -n +26 | xargs -n 1 zfs destroy -r
  zfs list -t snapshot -o name | grep rpool/data@ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
  zfs list -t snapshot -o name | grep rpool/data/ | tac | tail -n +26 | xargs -n 1 zfs destroy -r
  zfs list -t snapshot -o name | grep rpool/var-lib | tac | tail -n +26 | xargs -n 1 zfs destroy -r
fi
