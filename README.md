# OpenAR Skill Hub

Static skill catalog registry for OpenAR (`openar-cli` / `ora`).

OpenAR reads this repository's `skills.json` at a **pinned commit SHA** and verifies
each catalog entry's sha256 before use. Browsing the catalog never requires a model,
an account, or a Hub server — this repository is plain static data on GitHub.

## Layout

- `entries/skills/<id>/entry.json` — one directory record per skill (id, kind, source
  repo + exact revision, license, file manifest with sha256, review status, compat)
- `skills.json` — lightweight index generated from entries by `scripts/build-index`
  (never hand-edited)
- `schemas/` — the entry schema contract read by the OpenAR registry client
- `scripts/` — index generation and validation
- `.github/workflows/` — read-only validation CI

Entries land through pull requests validated by CI and reviewed before they reach
`main`. See `CONTRIBUTING.md` for the entry contract.

## How OpenAR uses an entry

1. **Discover** — OpenAR reads `skills.json` at a pinned commit (cached for offline
   use). Refreshing the catalog only refreshes that cache; it never installs, enables
   or runs anything.
2. **Install** — a person chooses an entry. OpenAR fetches exactly the files the
   entry lists at the entry's pinned `source.revision`, checks every sha256 and size,
   and stages them for approval. Nothing is active until the person approves that
   exact content hash.
3. **Use** — an approved skill is offered to agent sessions by name and short
   description; the skill body and its references are read only when a task needs
   them. A skill can be turned off per project.
4. **Update** — a newer entry is shown as an update with its differences (files,
   permissions note, dependencies). It is never applied automatically; a running
   session keeps the version it started with.
5. **Roll back** — the previous version is kept and can be restored.

OpenAR can also install a single skill directly from a GitHub repository using the
`owner/repo` / `…/tree/<ref>/<path>` source grammar of the open agent-skills
ecosystem. Such installs follow the same five steps, are marked unreviewed with an
unknown license, and do not appear in this catalog. Skills a person learns privately
from their own sessions never appear here either; listing a skill here is always a
separate, reviewed pull request.

## License

Repository metadata and scripts: MIT (see `LICENSE`). Each catalog entry carries its
own upstream license in its `entry.json`; entry content is not re-licensed or
re-hosted here unless the entry explicitly hosts it under `entries/skills/<id>/skill/`.
