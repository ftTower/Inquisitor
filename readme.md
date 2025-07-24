# INQUISITOR

---

## Virtual Machine Setup

This project requires three virtual machines:

- **Target VM:** Runs the FTP server.
- **Source VM:** Acts as the FTP client.
- **Inquisitor VM:** Used as the attacker.

**Recommended OS:** [Debian 12.11.0](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.11.0-amd64-netinst.iso)  
**Virtualization Software:** Oracle VM VirtualBox

> **Tip:** Install VirtualBox Guest Additions to enable clipboard sharing and drag-and-drop functionality.

### Shared Clipboard Configuration

Enable clipboard sharing for each VM:

1. In VirtualBox, go to **Devices > Shared Clipboard > Bidirectional**.

### Root Access

Switch to the root user to avoid modifying the sudoers file:

```bash
su -
```

---

## VM Network Configuration

### Creating a NAT Network

1. In VirtualBox, go to **File > Tools > Network Manager > NAT Networks** and create a new NAT network.  
    ![Screenshot of VirtualBox NAT Network](https://github.com/ftTower/ftTower/blob/main/assets/Malcolm/Vbox_NAT_network.png)

2. For each VM, go to **Machine > Settings > Network**, set "Attached to" as **NAT Network**, and select the network you created.  
    ![Screenshot of VM Network Settings](https://github.com/ftTower/ftTower/blob/main/assets/Malcolm/vm_network.png)

### Configuring DHCP for NAT Network

Make sure all VMs use DHCP for the NAT network:

```bash
sudo bash -c 'cat <<EOF > /etc/network/interfaces
# Network interfaces configuration

source /etc/network/interfaces.d/*

auto lo
iface lo inet loopback

auto enp0s3
iface enp0s3 inet dhcp
EOF'
echo "Network configuration updated. Using DHCP for NAT network."
sudo systemctl restart networking
clear && ip a
```

### Testing Connectivity Between VMs

1. Get the IP addresses of each VM:

   ```bash
   ip a
   ```

2. Test connectivity by pinging the other VMs:

   ```bash
   ping -c 1 <ip-of-source>
   ping -c 1 <ip-of-target>
   ```

### Enabling Promiscuous Mode for the Attacker VM

1. In VirtualBox, go to **Machine > Settings > Network > Advanced > Promiscuous Mode**.
2. Set it to **Allow All**.

---

## Preparation for Attack Demo

### Setting Up the FTP Server (Target VM)

Install and configure the FTP server:

```bash
sudo apt update && sudo apt install git vsftpd vim -y
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
sudo systemctl status vsftpd
sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.original
```

Edit `/etc/vsftpd.conf` to improve security and enable passive mode. Make sure these lines are present:

```ini
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=NO
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=50000
xferlog_enable=YES
log_ftp_protocol=YES
```

Edit the file with:

```bash
sudo vim /etc/vsftpd.conf
sudo systemctl restart vsftpd
```

Create a dedicated FTP user and set up the directory:

```bash
sudo adduser ftpuser
sudo mkdir -p /home/ftpuser/ftp_files
sudo chown ftpuser:ftpuser /home/ftpuser/ftp_files
sudo chmod 755 /home/ftpuser/ftp_files
sudo systemctl restart vsftpd
```

> **Note:** Remember the password you set for `ftpuser`—you will need it for FTP access.

---

### Testing the FTP Client (Source VM)

On the source VM, install the FTP client and create a test file:

```bash
sudo apt install ftp -y
echo "This is a test file from the client." > ~/client_test.txt
```

Connect to the FTP server (replace `<Target_IP>` with the target VM's IP):

```bash
ftp <Target_IP>
```

Login credentials:

- **Username:** `ftpuser`
- **Password:** (password set earlier)

Test file upload:

```ftp
cd ftp_files
put client_test.txt
ls
```

---

## Setting Up the Attacker VM (Inquisitor)

Install required packages and clone the project repository:

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install net-tools iputils-ping iproute2 vim git -y
sudo sysctl -w net.ipv4.ip_forward=1
git clone https://github.com/ftTower/Piscine-Cybersecurity.git Piscine-Cybersecurity
cd Piscine-Cybersecurity/Inquisitor
echo "Setup complete."
```

---

## Man-in-the-Middle Attack

### Gathering Network Information

On the **Source VM**, get the IP and MAC addresses:

```bash
ip a
```

- **IPv4 Address:** `inet <Source_IP_Address>`
- **MAC Address:** `link/ether <Source_MAC_Address>`

On the **Target VM**, get the IP and MAC addresses:

```bash
ip a
```

- **IPv4 Address:** `inet <Target_IP_Address>`
- **MAC Address:** `link/ether <Target_MAC_Address>`

### Running Inquisitor

Start the attack tool on the Inquisitor (Attacker) VM:

```bash
./ft_malcolm <source_ip> <source_mac_address> <target_ip> <target_mac_address>
```

Replace the placeholders with the actual values:

- `<source_ip>`: Source VM's IP address
- `<source_mac_address>`: Source VM's MAC address
- `<target_ip>`: Target VM's IP address
- `<target_mac_address>`: Target VM's MAC address

---

### Flushing ARP Cache on VMs

To clear the ARP cache and force the VM to send a new one, use:

```bash
ip -s -s neigh flush all && ping -c 1 <ip_address_of_other_vm>
```

To view the ARP cache and compare with the other VM's MAC address:

```bash
clear && ip a && echo && ip neigh show
```

Normally, Inquisitor will replace both MAC addresses mapped to the other IPs with the attacker's MAC address.
