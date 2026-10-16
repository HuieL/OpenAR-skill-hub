#!/usr/bin/env python3
"""Generate skills.json, .claude-plugin/marketplace.json, INSTALL.md,
SKILLS.md and the README summary from entries/skills/*/entry.json.

All of them are rebuildable projections of the entries; never hand-edit them.
- skills.json: the index OpenAR reads (`ora hub catalog`).
- .claude-plugin/marketplace.json: makes the skills this hub hosts
  installable with the vercel-labs/skills CLI (`npx skills add
  HuieL/OpenAR-skill-hub`) and listable as a Claude Code plugin marketplace.
- INSTALL.md: per entry, the exact pinned install command for OpenAR and for
  `npx skills`.
- SKILLS.md: the full list, grouped by category (icon, name, id, what it
  does, tags, where the files are, install command); the README carries only
  the counts per category and a link to it.
Run with --check to verify the committed files are current without writing.
"""

import hashlib
import json
import re
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import listing as listing_mod  # noqa: E402


def _root() -> pathlib.Path:
    """The registry tree to read: `--root <dir>` (CI runs the base branch's
    trusted scripts against a pull request's tree), else this checkout."""
    if "--root" in sys.argv:
        index = sys.argv.index("--root")
        if index + 1 >= len(sys.argv):
            sys.exit("--root needs a directory")
        return pathlib.Path(sys.argv[index + 1]).resolve()
    return pathlib.Path(__file__).resolve().parent.parent


ROOT = _root()
ENTRIES = ROOT / "entries" / "skills"


def build() -> dict:
    rows = []
    icons = listing_mod.load_icons()
    if ENTRIES.is_dir():
        for entry_path in sorted(ENTRIES.glob("*/entry.json")):
            raw = entry_path.read_bytes()
            entry = json.loads(raw)
            rows.append(
                {
                    "id": entry["id"],
                    "name": entry["name"],
                    "summary": entry["summary"],
                    "delivery": entry["delivery"],
                    "version": entry["version"],
                    "revision": entry["source"]["revision"],
                    "entryPath": entry_path.relative_to(ROOT).as_posix(),
                    "entrySha256": hashlib.sha256(raw).hexdigest(),
                    # Listing metadata (icon, search tags and the entry's
                    # categories, so a store can group without fetching every
                    # entry). Index rows are read leniently by every client;
                    # entry.json is not.
                    **listing_mod.listing_for(entry_path.parent, entry, icons),
                    **({"categories": entry["categories"]} if entry.get("categories") else {}),
                }
            )
    rows.sort(key=lambda row: row["id"])
    return {"schemaVersion": 1, "entries": rows}


def render(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


HUB_REPO = "HuieL/OpenAR-skill-hub"


def entries() -> list[dict]:
    if not ENTRIES.is_dir():
        return []
    return sorted(
        (json.loads(p.read_bytes()) for p in ENTRIES.glob("*/entry.json")),
        key=lambda e: e["id"],
    )


def hosted(entry: dict) -> bool:
    """The skill's files live in this repository (entries/<id>/skill)."""
    return (
        entry["source"]["repo"] == HUB_REPO
        and entry["source"]["path"] == f"entries/skills/{entry['id']}/skill"
    )


def upstream_plugins(rows: list[dict]) -> list[dict]:
    """One plugin per upstream repository and pinned commit, carrying only
    the listed skills (strict: false — the marketplace declares them, so the
    upstream repository needs no plugin manifest and unlisted skills there
    are not installed)."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for entry in rows:
        if not hosted(entry):
            groups.setdefault((entry["source"]["repo"], entry["source"]["revision"]), []).append(entry)
    plugins, names = [], set()
    for (repo, revision), group in sorted(groups.items()):
        name = re.sub(r"[^a-z0-9-]+", "-", repo.split("/")[1].lower()).strip("-")
        if name in names or name == "openar-skill-hub":
            name = re.sub(r"[^a-z0-9-]+", "-", repo.lower()).strip("-")
        names.add(name)
        plugins.append({
            "name": name,
            "source": {"source": "github", "repo": repo, "sha": revision},
            "description": f"{len(group)} skill{'s' if len(group) != 1 else ''} from {repo}, "
            f"pinned at {revision[:12]} as listed on the OpenAR Skill Hub.",
            "strict": False,
            "skills": sorted(f"./{e['source']['path']}" for e in group),
        })
    return plugins


def render_marketplace(rows: list[dict]) -> str:
    skills = [f"./entries/skills/{e['id']}/skill" for e in rows if hosted(e)]
    manifest = {
        "name": "openar-skill-hub",
        "owner": {"name": "HuieL"},
        "metadata": {
            "description": "Skills listed on the OpenAR Skill Hub. Generated by "
            "scripts/build-index.py: the skills hosted here, plus one plugin per "
            "upstream repository, pinned to the commit the hub reviewed.",
        },
        "plugins": [
            {
                "name": "openar-skill-hub",
                "source": "./",
                "description": "Every skill hosted in this repository.",
                "skills": skills,
            },
            *upstream_plugins(rows),
        ],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def npx_command(entry: dict) -> str:
    src = entry["source"]
    return f"npx skills add https://github.com/{src['repo']}/tree/{src['revision']}/{src['path']}"


def render_install(rows: list[dict]) -> str:
    lines = [
        "# Install a skill",
        "",
        "<!-- Generated by scripts/build-index.py from entries/; do not edit. -->",
        "",
        "Every command pins the entry's reviewed commit. In OpenAR the install",
        "is staged for your review and approval before anything is active; with",
        "the [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI it",
        "installs into your agents' skill folders directly.",
        "",
        "All skills this repository hosts at once:",
        "",
        "```bash",
        f"npx skills add {HUB_REPO}",
        "```",
        "",
        "As a Claude Code plugin marketplace:",
        "",
        "```",
        f"/plugin marketplace add {HUB_REPO}",
        "/plugin install openar-skill-hub@openar-skill-hub",
        "```",
        "",
        "| Entry | Version | License | Review | OpenAR | npx skills |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for e in rows:
        lines.append(
            f"| `{e['id']}` | {e['version'][:12]} | {e['license']} | {e['review']['status']} "
            f"| `ora hub install {e['id']}` | `{npx_command(e)}` |"
        )
    lines.append("")
    return "\n".join(lines)


CATALOG_START = "<!-- catalog:start (generated by scripts/build-index.py; do not edit) -->"
CATALOG_END = "<!-- catalog:end -->"


def catalog_row(e: dict, icons: dict) -> str:
    meta = listing_mod.listing_for(ENTRIES / e["id"], e)
    icon = icons.get(meta["icon"], {}).get("lucide", "Puzzle")
    src = e["source"]
    files = f"https://github.com/{src['repo']}/tree/{src['revision']}/{src['path']}"
    where = "in this repo" if hosted(e) else src["repo"]
    summary = e["summary"].split(". ")[0].replace("|", "\\|")[:140]
    tags = ", ".join(f"`{t}`" for t in meta["tags"])
    return (f"| `{icon}` | **{e['name']}**<br>`{e['id']}` {e['version'][:12]} | {summary} | {tags} "
            f"| [{where}]({files}) | `ora hub install {e['id']}` |")


def group_of(e: dict) -> str:
    return (e.get("categories") or ["other"])[0]


def group_label(group: str, icons: dict) -> str:
    # The icon whose primary category this is names the group.
    for icon in icons.values():
        if icon.get("categories", [None])[0] == group:
            return icon.get("label", group.title())
    return group.replace("-", " ").title()


def groups(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for e in rows:
        out.setdefault(group_of(e), []).append(e)
    return dict(sorted(out.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def render_skills_md(rows: list[dict]) -> str:
    icons = listing_mod.load_icons()["icons"]
    by = groups(rows)
    lines = ["# Skills in the OpenAR Skill Hub", "",
             "Generated by `scripts/build-index.py` from `entries/skills/*/entry.json` and `listing.json`; do not edit.", "",
             f"**{len(rows)} skills** in {len(by)} categories. Icon names are [lucide](https://lucide.dev/icons) icons; "
             "the files of an upstream entry stay in its repository at the pinned commit. "
             "Install with `ora hub install <id>` (staged for your approval) — see [INSTALL.md](INSTALL.md) for npx and the plugin marketplace.", "",
             " · ".join(f"[{group_label(g, icons)} ({len(es)})](#{g})" for g, es in by.items()), ""]
    for g, es in by.items():
        lines += [f'<a id="{g}"></a>', f"## {group_label(g, icons)} ({len(es)})", "",
                  "| | Skill | What it does | Tags | Files | Install |", "| --- | --- | --- | --- | --- | --- |"]
        lines += [catalog_row(e, icons) for e in es]
        lines.append("")
    return "\n".join(lines)


def render_catalog(rows: list[dict]) -> str:
    """The README's short summary; the full list is SKILLS.md."""
    icons = listing_mod.load_icons()["icons"]
    by = groups(rows)
    upstream = sorted({e["source"]["repo"] for e in rows if not hosted(e)})
    lines = [CATALOG_START, "",
             f"**{len(rows)} skills** ({sum(1 for e in rows if hosted(e))} hosted here, the rest pinned in "
             f"{len(upstream)} upstream repositories). **Full list: [SKILLS.md](SKILLS.md)**", "",
             " · ".join(f"[{group_label(g, icons)} ({len(es)})](SKILLS.md#{g})" for g, es in by.items()), "",
             CATALOG_END]
    return "\n".join(lines)


def render_readme(rows: list[dict]) -> str:
    text = (ROOT / "README.md").read_text()
    block = render_catalog(rows)
    if CATALOG_START in text and CATALOG_END in text:
        head, rest = text.split(CATALOG_START, 1)
        _, tail = rest.split(CATALOG_END, 1)
        return head + block + tail
    return text.replace("## Install a skill", "## Skills in this hub\n\n" + block + "\n\n## Install a skill", 1)


OUTPUTS = {
    "skills.json": lambda rows: render(build()),
    ".claude-plugin/marketplace.json": render_marketplace,
    "INSTALL.md": render_install,
    "README.md": render_readme,
    "SKILLS.md": render_skills_md,
}


def main() -> None:
    rows = entries()
    stale = []
    for name, render_fn in OUTPUTS.items():
        rendered = render_fn(rows)
        path = ROOT / name
        if "--check" in sys.argv:
            current = path.read_text() if path.exists() else ""
            if current != rendered:
                stale.append(name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
        print(f"wrote {name}")
    if stale:
        sys.exit(f"{', '.join(stale)} stale; run scripts/build-index.py and commit")
    if "--check" in sys.argv:
        print(f"skills.json, marketplace, INSTALL.md, README and SKILLS.md are current ({len(rows)} entries)")


if __name__ == "__main__":
    main()
