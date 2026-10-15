<!-- One topic per PR. CI runs scripts/validate.py read-only: no secrets, no
install step, nothing from your entry is executed. See CONTRIBUTING.md. -->

**This PR** (pick one): new entry · new revision of an entry · deprecation / high-risk marking · attribution fix · community data (featured, collection, creator)

**Entry id(s):**

### Checklist

- [ ] `source.revision` (and `upstream.revision`, if any) is an exact 40-hex commit, not a branch or tag.
- [ ] `files` lists every file of the skill at that revision with its sha256 and size; no symlinks, nothing outside the skill directory.
- [ ] `license` is the license the content actually carries, checked in the source repository; non-commercial or unclear terms are stated in `summary` / `permissionsNote`.
- [ ] `authors` are the original creators, verifiable from the source repository's commits, license or README. The submitter is recorded as `registrySubmitter`, never as an author unless they are one.
- [ ] `requires` and `permissionsNote` say what the skill needs. Tool permissions written inside SKILL.md are claims, not approvals.
- [ ] `python3 scripts/build-index.py` was run and the regenerated `skills.json` is committed in this PR; `python3 scripts/validate.py` passes locally.
- [ ] Nothing private: no tokens, credentials, personal data, or content from private sessions.
- [ ] A deprecation or high-risk marking changes only `review.status` and gives the reason below. Entries and history are never deleted.

**Reason / notes** (for markings and attribution fixes, include how you checked):
