FROM ubuntu:22.04 AS builder
RUN printf 'deb http://archive.ubuntu.com/ubuntu jammy main universe\ndeb http://archive.ubuntu.com/ubuntu jammy-updates main universe\n' > /etc/apt/sources.list \
    && apt-get update -o Acquire::Languages=none -o Acquire::Retries=2 \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
COPY vault.c /build/vault.c
COPY generated/vault_config.h /build/vault_config.h
RUN gcc -O2 -Wall -Wextra -o /build/prometheus-vault /build/vault.c

FROM ubuntu:22.04
RUN printf 'deb http://archive.ubuntu.com/ubuntu jammy main universe\ndeb http://archive.ubuntu.com/ubuntu jammy-updates main universe\n' > /etc/apt/sources.list \
    && apt-get update -o Acquire::Languages=none -o Acquire::Retries=2 \
    && apt-get install -y --no-install-recommends openssh-server ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash investigator && mkdir -p /run/sshd /root/prometheus \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
COPY --from=builder /build/prometheus-vault /usr/local/bin/prometheus-vault
COPY generated/flag.txt /root/prometheus/flag.txt
COPY entrypoint.sh /usr/local/bin/vault-entrypoint
RUN chown root:root /usr/local/bin/prometheus-vault /root/prometheus/flag.txt \
    && chmod 4755 /usr/local/bin/prometheus-vault \
    && chmod 700 /root/prometheus && chmod 600 /root/prometheus/flag.txt \
    && chmod 755 /usr/local/bin/vault-entrypoint
EXPOSE 22
ENTRYPOINT ["/usr/local/bin/vault-entrypoint"]
