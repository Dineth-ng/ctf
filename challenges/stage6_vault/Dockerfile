FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    python3 \
    gcc \
    make \
    binutils \
    gdb \
    file \
    vim \
    nano \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd
RUN mkdir -p /opt/vault

COPY vault_lock.c /tmp/vault_lock.c
COPY setup_vault.sh /tmp/setup_vault.sh

RUN bash /tmp/setup_vault.sh && rm /tmp/setup_vault.sh

# Configure SSH for password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
