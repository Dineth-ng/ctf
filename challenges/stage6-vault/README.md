# Stage 6: Prometheus Vault (organizer guide)

The proposed final target is a **dedicated Ubuntu 22.04 virtual machine** on a
host-only network. A VM is a computer inside your computer; host-only means
players can reach it from the lab host without exposing it to the internet.
The optional Docker version is for rehearsal if a VM is not yet available; it
should not be represented as the requested Ubuntu VM in the report.

## Preparation

Run `python scripts/build_lab.py` from the repository root. It generates a
private login password, vault flag, and build header. The vault code comes from
the two Stage 5 evidence files. Do not commit or distribute `generated/` or
`.organizer/`. The visible C source is deliberately inspectable, but the
generated code and flag are not part of the public repository.

## VM installation

1. Install a fresh Ubuntu 22.04 VM in VirtualBox. Create a **host-only adapter**.
   Disconnect NAT and bridged adapters after installing packages. Record its
   host-only IP address. Do not forward SSH to a public network.
2. While package installation is possible, copy this repository into a
   root-owned build directory on the VM (for example `/root/ctf-build`) and
   run `sudo bash challenges/stage6-vault/provision-ubuntu.sh` from the repo root.
   The script creates the low-privilege `investigator` account, installs SSH,
   builds the small vault program, and makes the final flag and generated
   secrets root-readable only. Never place the private source in that user's
   home directory.
3. Verify that the VM has no NAT/bridged adapter, then take a clean VirtualBox
   snapshot. Tell players only its host-only IP and that the login details are
   in Stage 5 evidence. Do **not** hand out `generated/` or the manifest.
4. From the lab host, SSH to `investigator@VM_IP`. The password is in the
   deleted Stage 5 note. `cat /root/prometheus/flag.txt` should fail. Running
   `/usr/local/bin/prometheus-vault` with an incorrect code should reject it.
   The correct two-part code unlocks an **audit response** prompt; inspecting
   the binary's transformation is needed to calculate that response and reveal
   the final flag. An incorrect audit response must fail.

The set-user-ID bit makes this one program run with the file owner's (root's)
access rights. It is intentionally narrow: no shell commands, file paths, or
other user-controlled operations are passed to it. Never install this program
on an ordinary laptop/server outside the disposable lab VM.

## Optional container rehearsal

If the VM is not ready, run:

```powershell
docker compose --profile vault-container up -d --build stage6-vault
```

Then SSH to `127.0.0.1` port `2226` as `investigator`, using the password from
the recovered disk note. The container is not a substitute for VM evidence.
To stop it, run `docker compose --profile vault-container stop stage6-vault`.

## Reset

For the VM, restore the clean snapshot and verify SSH and the flag permissions.
For the rehearsal container, run `docker compose --profile vault-container up
-d --no-deps --force-recreate stage6-vault`. CTFd scores are not erased by
either reset. Run `python tests/stage6_smoke.py` to test permission denial,
wrong input, and correct input on the container. Repeat manual checks on the VM.
