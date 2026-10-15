# Example: contributing a standard skill

A standard skill is a directory with a `SKILL.md` (YAML frontmatter `name`
and `description`, then the instructions) and optional `scripts/`,
`references/` and `assets/`. This is the same layout the open agent-skills
tooling uses (`npx skills init`), so one skill works across hosts.
`example-skill/` is a starting point.

The hub never copies your repository and never runs anything from it. An
entry points at your repository at an exact commit and lists every file
with its sha256; OpenAR installs exactly those bytes after the user
approves them.

## Steps

1. **Write the skill** in your own GitHub repository (copy
   `example-skill/`, rename the directory and the frontmatter `name`).
   Keep private paths, names, tokens and session data out of it.
2. **Check what a client sees** at the commit you want to publish:

   ```sh
   ora hub peek https://github.com/<you>/<repo>/tree/<40-hex commit>/<skill-dir>
   ```

   It lists the skills found, their files and sizes, and refuses symlinks
   and oversized trees, the same checks an install applies.
3. **Draft the entry** from that commit:

   ```sh
   ora hub learn entry-draft https://github.com/<you>/<repo>/tree/<40-hex commit>/<skill-dir> \
     --id <you>.<skill> --version 1.0.0 --license <SPDX> --author "<your name>" --github <you>
   ```

   It prints an `entry.json` with the pinned source and the full file
   manifest. Without `ora`, write it by hand against
   `schemas/skill-entry.schema.json`;
   `entries/skills/hub.human-writing/entry.json` is a complete real entry.
4. **Add it** as `entries/skills/<id>/entry.json`, run
   `python3 scripts/build-index.py` and `python3 scripts/validate.py`, and
   open a pull request with both the entry and the regenerated
   `skills.json`.

## What review means here

CI only validates the catalog (ids, paths, pins, hashes, license fields);
it never executes your skill. A maintainer's `review.status` records what
a person looked at, at which revision. Listed is not endorsed, and
unreviewed is not an accusation. Credit is recorded per role: `authors`
(who wrote it), `adapters` (who adapted it for OpenAR), `registrySubmitter`
(who filed the entry). See `CONTRIBUTING.md`.
