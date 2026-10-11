# Stage 5: Tracing the Exfiltration (organizer guide)

This stage has two scored parts. A **PCAP** is a saved copy of network packets;
a **disk image** is a byte-for-byte copy of a small storage device. Everything
here is fictional and generated locally. Do not upload this guide as a player
file because it explains the answers.

## Build and hand out

From the repository root, run `python scripts/build_lab.py`. It creates:

- `files/NH-048-traffic.pcap` for Stage 5A;
- `files/NH-048-disk.img` for Stage 5B;
- `.organizer/lab-secrets.json` with the private answers.

Upload the two evidence files to the matching CTFd challenges via
`python scripts/register_ctfd.py`. Do not upload the private manifest or this
source/generator folder. The same build command may be rerun without changing
the flags. Do not regenerate the manifest after registering challenges.

## What a player discovers

The capture contains ordinary-looking HTTP requests and two POST requests to
the fictional archive server. Their bodies are two parts of a Base64 message,
arriving in reverse order. The `X-Archive-Part` header tells the order. Decode
the assembled body to recover the first flag and the first half of a vault code.

The disk is a FAT12 floppy image. Its root directory includes a deleted ZIP
entry. The entry still points to the data cluster because no new file overwrote
it. Recover the archive, then read its note to find the second flag, vault
login, and second code half. The executable asks for these fragments and an
audit response whose transformation must be learned from the binary. A plain
text scan of the disk should not reveal the flag because the note is compressed
inside the archive. The two code halves join with a hyphen for the first Stage
6 prompt.

For organizer verification only:

```powershell
python challenges/stage5-forensics/solve.py
```

Compare the output with `.organizer/lab-secrets.json` without putting either in
Git. A wrong order for the network halves must not decode to the message.
Deleting a directory entry is not secure erasure; real storage recovery depends
on whether its data was overwritten. These files are safe teaching simulations,
not captures from a real victim.

## Reset

The evidence is static, so no service reset is needed. Rerun
`python scripts/build_lab.py` if a local copy was lost. CTFd keeps its existing
scores. If you rotate private flags intentionally, update CTFd and redistribute
new evidence as a coordinated organizer task.
