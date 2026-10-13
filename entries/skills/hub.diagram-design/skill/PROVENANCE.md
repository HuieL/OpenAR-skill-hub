# Provenance

This skill is carried from the third-party repository
`cathrynlavery/diagram-design` at commit `7a2e22170ee838e859d8142ba825d83f8b6375e6`
(MIT; see `LICENSE` in this directory, copied verbatim from the upstream
repository root). It is vendored as a default-on, per-project toggleable
built-in skill under its upstream name `diagram-design` (no `ora-` prefix:
the name marks it as third-party).

Recorded transformations from the upstream `skills/diagram-design/` tree —
everything not listed here is carried verbatim:

1. **Examples dropped.** The upstream `assets/` directory ships 204
   `example-*.html` demo files (4.0 MB); none are carried. References that
   mention `assets/example-<type>*.html` are describing those dropped demos;
   the `template*.html`, `icons.html` and `index.html` assets they build on
   are carried.
2. **Frontmatter normalized.** The upstream `SKILL.md` frontmatter carries an
   823-character `description`, plus `license: MIT` and `metadata.version`
   keys. Our skill format requires a single-line, JSON-quoted description of
   at most 400 characters and only `name`/`description` keys, so the
   description was rewritten (routing boundary with `ora-figures`: its
   bar/line/scatter/heatmap types are for illustrative and concept data;
   run-result plots belong to `ora-figures`) and the license/version keys
   moved out of the frontmatter. The original
   upstream description, preserved for the record:

   > Create branded architecture, architecture delta, IT current-state, flowchart, sequence, state machine, ER/data model, timeline, swimlane, quadrant, radar/spider, polar chart (polar/radial lollipop), loop/flywheel, nested, tree, org chart, layer stack, exploded axonometric, axonometric plan, Venn, pyramid/funnel, treemap and marimekko, heatmap, bar and dumbbell, waterfall, line (slopegraph, ridgeline, streamgraph, bump), Gantt and scatter charts (bubble, beeswarm), high-level, process, medallion, data flow, DP integration, DP security matrix, Sankey, fishbone, Wardley map, kanban, user journey, deployment, dependency graph, UML class, story map, or database schema diagrams as HTML/SVG/PNG, with .drawio, Mermaid, and .excalidraw import, plus lifecycle phase maps, block decomposition trees, and onboarding guidance.

   Upstream `metadata.version` at the pinned commit: `2.6`.

3. **This file added** (`PROVENANCE.md`); upstream does not carry it.
4. **`THIRD_PARTY_LICENSES.md` carried verbatim** from the upstream repository
   root (Tabler Icons, Simple Icons, log-z/logos, Devicon, Instrument Serif,
   one-off sourced icons, trademarks note). Its mentions of
   `scripts/vendor/` and upstream `skills/diagram-design/` paths describe the
   upstream tree; the Devicon and one-off-icon entries cover source assets
   not carried here.
5. **"OpenAR host notes" section added** at the top of the `SKILL.md` body
   (OpenAR deployment rulings: project-local `.diagram-design/profile.md`
   profile storage instead of `~/.diagram-design`, no reads of home-directory
   skill folders, network-permission and ask-first rules for website
   onboarding, and a note that the dropped `example-*.html` demos must not be
   opened). Everything below that section is upstream text.
