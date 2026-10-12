# OpenAR Skill Hub

Static skill catalog registry for [OpenRA](https://github.com/HuieL/OpenRA) (`openar-cli` / `ora`).

OpenRA reads this repository's `skills.json` at a **pinned commit SHA** and verifies
each catalog entry's sha256 before use. Browsing the catalog never requires a model,
an account, or a Hub server — this repository is plain static data on GitHub.

## Layout

- `entries/skills/<id>/entry.json` — one directory record per skill (id, kind, source
  repo + exact revision, license, file manifest with sha256, review status, compat)
- `skills.json` — lightweight index generated from entries by `scripts/build-index`
  (never hand-edited)
- `schemas/` — the entry schema contract read by the OpenRA registry client
- `scripts/` — index generation and validation
- `.github/workflows/` — read-only validation CI

The catalog starts empty; entries land through PRs validated by CI. See
`CONTRIBUTING.md` for the entry contract, and the OpenRA repository's
`docs/skill-extension-hub-design.md` for the design.

## License

Repository metadata and scripts: MIT (see `LICENSE`). Each catalog entry carries its
own upstream license in its `entry.json`; entry content is not re-licensed or
re-hosted here unless the entry explicitly hosts it under `entries/skills/<id>/skill/`.
