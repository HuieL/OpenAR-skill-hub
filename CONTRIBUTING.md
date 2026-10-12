# Contributing to the OpenAR Skill Hub

This repository is a static catalog. OpenRA reads `skills.json` at a pinned
commit SHA and verifies each entry's sha256 before use. There is no server, no
account, and no install script to run here.

## Adding an entry

1. Host your skill in your own repository (a `SKILL.md` plus optional
   `scripts/`, `references/`, `assets/`). This hub does not copy third-party
   repositories.
2. Create `entries/skills/<id>/entry.json` following
   `schemas/skill-entry.schema.json`. The required facts:
   - `id` — namespaced identity (e.g. `openra.diagram-design`), equal to the
     directory name, globally unique, never reused;
   - `source` — `owner/name`, the skill's subdirectory, and an exact 40-hex
     commit SHA. `main`/`latest`/mutable tags are never accepted as a pin;
   - `files` — the complete manifest of the skill's files at that revision,
     each with sha256 and size (cap: 2 MiB per entry). Required for
     `delivery: hub` entries; `delivery: bundled` entries ship with the app
     and carry no files manifest;
   - `license` — SPDX id; the entry must state the license its content
     actually carries.
3. Run `python3 scripts/build-index.py` and commit the regenerated
   `skills.json` together with your entry.
4. Open a PR. CI runs `scripts/validate.py` (read-only, no secrets, no
   install step; it never executes anything from your entry).

Maintainer-owned small skills may host their content directly under
`entries/skills/<id>/skill/`; every hosted file must then be listed in `files`
with a matching hash. Symlinks are rejected everywhere.

## Attribution

Original author, OpenRA adapter, and registry submitter are three different
roles and are recorded separately: `authors` (the original creators, with
names and optional GitHub logins), `adapters` (who adapted it for OpenRA),
and `registrySubmitter` (who filed the entry). Submitting a manifest does
not make you an author; authorship is checked against the source repository's
commits, license, or README during review, and corrections go through a PR.

## What review means

`review.status` records what a human looked at, and `reviewedRevision` pins
which revision that covered. `unreviewed` is not an accusation and `reviewed`
is not a guarantee; neither grants anything on a user's machine. Declarations
inside a `SKILL.md` (such as `allowed-tools`) are claims, not approvals.

## Updates and removal

A new upstream revision is a new `source.revision` plus a new `files` manifest;
older revisions stay in git history. Deprecation or a high-risk marking changes
`review.status` with a reason — entries and history are not silently deleted.
