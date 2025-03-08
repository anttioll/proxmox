import random
import string
import subprocess
from os import environ
from time import sleep
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI


load_dotenv()
proxmox_host: str = environ.get("PROXMOX_HOST")
proxmox_user: str = environ.get("PROXMOX_USER")
proxmox_password: str = environ.get("PROXMOX_PASSWORD")
proxmox = ProxmoxAPI(host=proxmox_host, 
                     user=proxmox_user, 
                     password=proxmox_password, 
                     verify_ssl=False, 
                     )


def authenticate(username: str, password: str) -> bool:
    try:
        if proxmox.access.ticket.post(username=username, password=password, path="/", privs="Sys.Console"):
            return True
        else:
            return False
    except:
        return False


def create_vms() -> None:
    """
    Luo opiskelijoiden virtuaalikoneet VMID:llä 100 - 159. 
    Koneet 100 - 129 luodaan solmulle "proxmox1" ja
    koneet 130 - 159 solmulle "proxmox2".
    Koneiden nimiksi tulee:
        kaouser1-vm1, kaouser1-vm2, kaouser1-vm3
        ...
        kaouser20-vm1, kaouser20-vm2, kaouser20-vm3
    Asettaa koneet replikoitumaan toiselle solmulle.
    """
    newvmid: int = 100
    node: str = ""
    replication_node: str = ""
    vlantag: int = 1001
    for usernumber in range(1, 21):
        for vmnumber in range(1, 4):
            if usernumber < 11:
                node = "proxmox1"
                replication_node = "proxmox2"
            else:
                node = "proxmox2"
                replication_node = "proxmox1"
            proxmox.nodes(node).qemu.create(
                    vmid=newvmid,
                    agent=1,
                    bios="ovmf",
                    boot="order=ide0;ide1;scsi0;sata0;net0",
                    cores=4,
                    cpu="host",
                    efidisk0="file=vm:1,efitype=4m,pre-enrolled-keys=1,size=1M",
                    ide0="none,media=cdrom",
                    ide1="none,media=cdrom",
                    machine="pc-q35-9.0",
                    memory=6144,
                    name = "kaouser" + str(usernumber) + "-vm" + str(vmnumber),
                    net0 = "e1000,bridge=vmbr0,firewall=1",
                    net1 = "e1000,bridge=vmbr0,tag=" + str(vlantag) + ",firewall=0",
                    numa=0,
                    ostype="win11",
                    sata0="file=vm:100,cache=writeback,discard=on,size=100G", 
                    scsi0="file=vm:100,cache=writeback,discard=on,size=100G", 
                    scsihw="virtio-scsi-pci",
                    tpmstate0="file=vm:1,size=4M,version=v2.0",
                    )
            sleep(15)
            proxmox.cluster.replication.post(id=str(newvmid)+"-0", target=replication_node, type="local")
            newvmid = newvmid + 1
            sleep(10)
        vlantag = vlantag + 1


def delete_vms() -> None:
    node: str = ""
    nodes: list = ["proxmox1", "proxmox2"]
    for vmid in range(100, 160):
        if vmid < 130:
            node = "proxmox1"
        else:
            node = "proxmox2"
        vmid = str(vmid)
        try:
            proxmox.nodes(node+"/qemu/"+vmid+"/status/stop").post()
            sleep(5)
            proxmox.nodes(node+"/qemu/"+vmid).delete(purge=1)
            for node in nodes:
                proxmox.nodes(node+"/storage/vm/content/vm-"+vmid+"-disk-0").delete()
                proxmox.nodes(node+"/storage/vm/content/vm-"+vmid+"-disk-1").delete()
                proxmox.nodes(node+"/storage/vm/content/vm-"+vmid+"-disk-2").delete()
                proxmox.nodes(node+"/storage/vm/content/vm-"+vmid+"-disk-3").delete()
        except:
            pass
        sleep(5)


def reset_passwords() -> None:
    """
    Nollaa kaikkien opiskelijakäyttäjien salasanat
    """

    adjectives1 = ["kymmenen_sanan_lista"]

    adjectives2 = ["kolmenkymmenen_sanan_lista"]

    words = ["kolmenkymmenen_sanan_lista"]

    with open("/home/proxmox/passwords.txt", "w") as file:
        for usernumber in range(1, 21):
            user: str = "kayttaja" + str(usernumber) + "@pve"
            password: str = adjectives1[random.randint(0, 9)] + "-" + adjectives2[random.randint(0, 29)] + "-" + words[random.randint(0, 29)]
            proxmox.access.password.put(password=password, userid=user)
            file.write(f"\n{user}: {password}\n")


def set_permissions() -> None:
    """
    Bash-skripti ylikirjoittaa tiedostolla '/etc/pve/user.cfg.defaults', 
    jossa Proxmoxia konfiguroitaessa asetetut käyttöoikeudet, käyttäjät, ryhmät ym.
    tiedoston 'etc/pve/user.cfg', jossa olemassaolevat käyttöoikeudet.
    """
    subprocess.run(["ssh", "-t", "root@IP", "'/root/skriptit/luo_kayttooikeudet.sh'"], shell=False)


def apply_firewall_rules() -> None:
    """
    Bash-skripti kopioi palomuurisäännöt tekstitiedosta '/etc/pve/firewall/vm-palomuufw
    kaikille opiskelijakoneille VMID:llä 100 - 159 tiedostoihin '/etc/pve/firewallVMID.fw'.
    """
    subprocess.run(["ssh", "-t", "root@IP", "'/root/skriptit/luo_palomuurisaannot.sh'"], shell=False)
