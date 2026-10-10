# Operation NightHawk: The GhostByte Files

IE3132 Penetration Testing - CTF Play Box Implementation

## Overview

Operation NightHawk is a story-driven Capture The Flag environment
based on a fictional cyberattack against NexaCore Dynamics.

Participants act as junior penetration testers investigating the
GhostByte threat group.

The CTF contains six progressive stages.

## Challenges

1. The Digital Footprint - OSINT / Reconnaissance
2. The Hidden Message - Steganography
3. Encrypted Correspondence - Cryptography
4. The Backdoor Portal - Web Security
5. Tracing the Exfiltration - Digital Forensics & Networking
6. The Prometheus Vault - Linux Security & Reverse Engineering

## Architecture

The project uses:

- CTFd
- Docker
- Docker Compose
- PHP
- MySQL
- Nginx
- Python
- Ubuntu VM

## Flag Format

All flags use:

NH{flag_text}

## Status

Developer and tester action guidelines for **Stages 1, 2, 3, and 4** are in
[the Stage 1–4 testing guide](docs/testing/stages-1-4.md). It includes preparation,
walkthrough commands, expected flags and handoff clues, failure checks, and resets.
This guide contains solutions and is for organizers only.

Stage 4 is implemented. Start it with:

```bash
docker compose up -d --build --wait stage4-web stage4-db
```

Open http://127.0.0.1:8084/legacy/auth/ . See [the Stage 4 guide](challenges/stage4-web/README.md) for configuration, CTFd setup, validation, and reset instructions.
