# Stage 6 Ubuntu VM

The vault implementation lives in `../stage6-vault`. This directory documents
the dedicated VM deployment; the Docker container is a separate rehearsal.

Create an Ubuntu 22.04 VM in VirtualBox with 2 GB RAM and a 20 GB disk. Use
NAT temporarily to install Ubuntu and packages, and add a host-only adapter
for the lab. Use an organizer administrator account, not `investigator`,
during installation.

On the host, from the repository root:

```bash
python3 scripts/build_lab.py
python3 scripts/package_stage6_vm.py
scp .organizer/stage6-vm-installer.tar.gz ADMIN@VM_IP:~/
```

Replace `ADMIN` and `VM_IP` with the organizer account and host-only IP. If
SSH is not installed yet, run `sudo apt update` and `sudo apt install
openssh-server` in the VM console before copying. The archive contains private
answers and must never be a player download.

In the VM's organizer account:

```bash
sudo mkdir -p /root/ctf-build
sudo chmod 700 /root/ctf-build
sudo tar -xzf ~/stage6-vm-installer.tar.gz -C /root
sudo bash /root/ctf-build/challenges/stage6-vault/provision-ubuntu.sh
rm ~/stage6-vm-installer.tar.gz
```

Shut down the VM and disable NAT and bridged adapters in VirtualBox. Retain
only the host-only adapter. Boot it and record its address with `ip -4 addr`.
Take a clean snapshot after verification.

From the host:

```bash
ssh investigator@VM_IP
cat /root/prometheus/flag.txt
/usr/local/bin/prometheus-vault
```

Use the password recovered from Stage 5. Direct flag access must fail. Check
that a wrong recovery code fails, a correct code with a wrong audit response
fails, and the correct code and audit response print the final flag. See
`../stage6-vault/README.md` for the recovery sequence. Record these checks on
the VM separately from the Docker smoke checks.

Restore the clean VM snapshot between player sessions. If VirtualBox reports
that `vboxdrv` is unavailable, repair the host's VirtualBox installation before
attempting to start the VM.
