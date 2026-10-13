# Provenance

This skill is an OpenAR-adapted carry of two MIT-licensed Vercel Labs
sources:

- The skill shell (frontmatter and workflow) comes from
  `vercel-labs/agent-skills` at commit
  `063bee94c3f4df8453406c830b0a7df0f2860278`, path
  `skills/web-design-guidelines/SKILL.md`.
- The review rules are carried verbatim from
  `vercel-labs/web-interface-guidelines` at commit
  `434b7f91364665f2f733b310ec54809bf8f37937`, path `command.md`, now at
  `references/command.md`. That repository's MIT `LICENSE` is carried as
  `LICENSE`.

The only modification to the shell: the workflow no longer fetches
`command.md` from the upstream repository's mutable `main` branch at review
time; it reads the vendored, pinned copy instead. Everything else is
upstream text.
