#!/bin/sh
set -eu
password_file=/run/secrets/vault_password
if [ ! -r "$password_file" ]; then
    echo 'Vault password secret is missing.' >&2
    exit 1
fi
printf 'investigator:%s\n' "$(cat "$password_file")" | chpasswd
exec /usr/sbin/sshd -D -e
