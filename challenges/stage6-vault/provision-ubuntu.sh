#!/usr/bin/env bash
# Run as root inside a dedicated Ubuntu 22.04 VM with only a host-only adapter.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
if [[ $EUID -ne 0 ]]; then
  echo 'Run this script with sudo inside the lab VM.' >&2
  exit 1
fi
for file in "$root/generated/vault_config.h" "$root/generated/flag.txt" "$root/generated/password.txt"; do
  [[ -f "$file" ]] || { echo "Missing generated file: $file" >&2; exit 1; }
done
repo_root="$(cd "$root/../.." && pwd)"
if [[ -d "$repo_root/.organizer" ]]; then
  chown -R root:root "$repo_root/.organizer"
  chmod 700 "$repo_root/.organizer"
  find "$repo_root/.organizer" -type f -exec chmod 600 {} +
fi
chown -R root:root "$root/generated"
chmod 700 "$root/generated"
find "$root/generated" -type f -exec chmod 600 {} +
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc libc6-dev openssh-server
id investigator >/dev/null 2>&1 || useradd -m -s /bin/bash investigator
printf 'investigator:%s\n' "$(cat "$root/generated/password.txt")" | chpasswd
gcc -O2 -Wall -Wextra -o /usr/local/bin/prometheus-vault "$root/vault.c"
chown root:root /usr/local/bin/prometheus-vault
chmod 4755 /usr/local/bin/prometheus-vault
install -d -m 700 -o root -g root /root/prometheus
install -m 600 -o root -g root "$root/generated/flag.txt" /root/prometheus/flag.txt
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
systemctl enable --now ssh
systemctl restart ssh
echo 'Vault provisioned. Disconnect this VM from NAT/bridged networks before players connect.'
