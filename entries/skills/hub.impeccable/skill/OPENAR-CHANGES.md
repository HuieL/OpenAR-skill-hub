# Changes in the OpenAR Skill Hub carry

Source: pbakaus/impeccable@5cb95eea9c96479f57afe0732a45470d30183326,
`.agents/skills/impeccable/` (generated from the repository's `skill/`),
Apache-2.0 (LICENSE, NOTICE.md). Modified by HuieL, 2026-10-23:

- `scripts/impeccable`, `scripts/impeccable.cmd`: export
  `IMPECCABLE_NO_UPDATE_CHECK=1`, so the engine never asks impeccable.style
  for a newer release or prompts `npx impeccable update`.
- `reference/doctor.md`: update through the Skill Hub, not `npx`.
- `reference/hooks.md`: the hook is installed at project scope only.

Unchanged: the engine binary is still fetched once per pinned version from
the upstream GitHub release and verified against its `.sha256` sidecar
(cached under `~/.impeccable`, or `IMPECCABLE_HOME`); set `IMPECCABLE_BIN`
to use a locally built engine instead.
