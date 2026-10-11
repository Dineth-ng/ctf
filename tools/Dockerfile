FROM ubuntu:22.04
RUN printf 'deb http://archive.ubuntu.com/ubuntu jammy main universe\ndeb http://archive.ubuntu.com/ubuntu jammy-updates main universe\n' > /etc/apt/sources.list \
    && apt-get update -o Acquire::Languages=none -o Acquire::Retries=2 \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libimage-exiftool-perl steghide && rm -rf /var/lib/apt/lists/*
WORKDIR /work
