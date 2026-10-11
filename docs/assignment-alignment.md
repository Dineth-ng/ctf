# Assignment alignment and honest limitations

The first report proposed six connected stages across reconnaissance,
steganography, cryptography, web security, forensics/networking, and Linux
security/reverse engineering. This implementation keeps that order and the
GhostByte/Prometheus storyline. Stage 5 is split into two CTFd entries (5A and
5B), not an unrelated seventh story stage. Stage 5 is moderate-hard; Stage 6
is the hard final stage.

Differences and decisions to disclose in the final report:

- The original repository contained only Stages 1–4. The Stage 1 image lacked
  its intended metadata, and the checked-in Stage 2 stego file contained an
  older note. Both must be regenerated/checked before a player run.
- Assignment 01's contribution table calls Stage 2 "LSB steganography," but the
  implemented challenge uses Steghide's embedding method. Describe the actual
  method accurately; do not claim an LSB implementation.
- Assignment 01 labels Stage 5 Hard while Assignment 02 explicitly requires
  Moderate–Hard. Treat the later brief as the assessment requirement and
  explain this difficulty adjustment as a change.
- The Stage 6 Docker service is a development rehearsal. The proposal calls
  for an Ubuntu VM, so the assessed deployment needs a real VM, host-only
  networking, a clean snapshot, and evidence of both access denial and success.
- Stage 5 uses **generated fictional** evidence, not live packet capture or a
  disk copied from a victim. The proposed "damaged disk" is implemented as a
  valid FAT12 image with a deleted compressed archive; this makes recovery
  repeatable and safe while preserving the forensic learning objective.
- The public source repository reveals Stage 1–4 solutions. It is not suitable
  as a player download. CTFd should serve only player artifacts.
- The CTFd instance is local. An organizer must complete first-run setup,
  create an API token, register challenges, and test actual flag submissions.

Human work still required for submission: each member must genuinely review,
understand, and contribute their claimed original script; capture evidence of
working challenge play and CTFd scoring; and verify the Ubuntu VM and network
isolation. Assignment 02 requires **no new written report**. It does require
one group package containing the box files, source, contribution evidence, and
a single real-environment video of at most 20 minutes. All four members must
participate. The demonstration must be delivered in their own words with no AI
tool or AI-prepared explanation used in the demonstration. No AI-prepared
demonstration script is included here.
