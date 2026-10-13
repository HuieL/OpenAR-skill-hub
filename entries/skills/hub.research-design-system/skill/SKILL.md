---
name: research-design-system
description: "Pick and apply one pinned design-system analysis (a design-md reference) as the design reference for an OpenAR research output. Use when the user wants a design language or reference for a website or another rendered output, asks what design references are available, or mentions design-md. Not a brand installer: one material is picked by the user, fetched once, hash-verified, and distilled into a reviewable token candidate."
version: 1.0.0
---

# Research Design System — a design-reference selector

This skill is a thin, generic workflow over a pinned catalog of
design-system analyses. The catalog lives in
[`references/design-md-index.md`](references/design-md-index.md): 84
`DESIGN.md` analyses carried by reference from
`VoltAgent/awesome-design-md` at commit
`c7c1bada4eda972236d124e06ee58df129a9266b` (MIT), subdirectory
`design-md/`. Each analysis is a third-party reading of one brand's visual
language — colors, typography, spacing, component voice.

What these materials are **not**: they are not skills, not `SKILL.md`
files, not official brand themes, and not brand assets. A brand analysis
is not brand endorsement or authorization. There is one generic selector
here, not one installer per brand.

## Hard rules

1. **The user picks.** Present a selection; never fetch a document body
   just to browse. After a pick, fetch only that one `DESIGN.md`.
2. **Verify before use.** The fetched file's sha256 must match the index.
   A mismatch means the pin moved — stop and report, do not proceed with
   the unverified text.
3. **Upstream is read-only.** Your working copy and the tokens you derive
   from it are separate artifacts. Record the projection: which material,
   which pinned revision, which passages produced which tokens.
4. **No silent overwrites.** Never overwrite an existing `DESIGN.md` or
   design file in the user's project. Propose a reviewable candidate;
   apply only after the user confirms, and bind it to the output revision
   it was confirmed for.
5. **Updates are suggestions.** A newer upstream revision only prompts a
   candidate; it never replaces a design in use, an output, or any
   session context on its own.
6. **No brand assets.** Do not copy logos, photographs or font files from
   the analyzed brand, and never present an analysis as the brand's
   official theme.

## Workflow

1. **Discover.** Read the index. Present a short selection matched to the
   user's ask (or search the one-line readings for a vibe, e.g.
   "editorial", "developer tool", "high-contrast crypto"). Always state
   provenance when presenting: analysis by the VoltAgent
   `awesome-design-md` project (MIT), pinned revision, adapted for OpenAR
   by the Skill Hub — the analyzed brand is not the author and has not
   endorsed anything.
2. **Pick.** The user names one material.
3. **Fetch and cache.** Fetch
   `https://raw.githubusercontent.com/VoltAgent/awesome-design-md/c7c1bada4eda972236d124e06ee58df129a9266b/design-md/<slug>/DESIGN.md`,
   verify the sha256 against the index, and cache the verified file
   locally. After this one fetch, no further network access is needed.
4. **Distill.** Turn the prose analysis into a reviewable candidate:
   concrete tokens (color values, type pairing, spacing rhythm, component
   notes), each traced to the passage it came from. Present the candidate
   and wait.
5. **Bind.** After confirmation, record the binding — material slug,
   pinned revision, verified hash, output revision — alongside the
   applied tokens. Auto-apply nothing.

## Compatibility

Any OpenAR research output that renders HTML/CSS (project website, Web).
For print or slides, check that output's own constraints before applying
a web-oriented reference.
