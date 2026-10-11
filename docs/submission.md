# Submission packaging checks

Assignment 02 asks for one package named with the **four student index
numbers**, not a new written report. The package needs the real-environment
video (MP4, at most 20 minutes), deployable box files, source code, and
evidence identifying each member's contribution. Follow the exact courseweb
upload instructions and size limits in the brief.

Before making that package:

1. Rebuild and test all player files. Run the local service, reset, and
   submission checks in `docs/testing/results.md`; replace every pending cell
   with a real observation or an honest limitation.
2. Include this repository or a branch export, the generated **player** PCAP
   and disk image, the generated Stage 6 build inputs under a private organizer
   folder, and the finished Ubuntu VM image or a verified way to rebuild it.
   The lecturer must be able to deploy the box. Do not assume GitHub alone
   contains generated files, because those are intentionally ignored.
3. Keep live passwords, flags, and the CTFd admin token in an organizer-only
   part of the handoff, not in the public GitHub branch or player downloads.
   If using a VM export, verify that the private build tree is root-readable
   only and that the `investigator` account cannot read the final flag directly.
4. Include a truthful contribution record: links or exported Git history,
   each member's own script, and actual test logs/screenshots. Do not attribute
   an AI-generated script to a member as if they wrote it independently.
5. Have all four members carry out the demonstration in their own words.
   Do not use AI tools, AI-generated explanations, or a prepared AI script
   during the recording. The recording must show the real running environment,
   not slides or mock-ups, and must meet the brief's camera/voice and editing
   rules.

The package cannot be finalized until the VM, all CTFd challenge entries,
actual flag submissions, and contribution evidence have been verified.
