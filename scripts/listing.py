#!/usr/bin/env python3
"""Listing metadata for Skill Hub entries: the icon and the search tags.

An entry may carry entries/skills/<id>/listing.json:

    {"icon": "<id in icons.json>", "tags": ["...", "..."]}

Both fields are optional. When `icon` is absent the best icon is picked from
the entry's categories and tags (strongest), then its name and summary
(keywords). Tags are the listing's tags plus the entry's categories. The
picked values go into skills.json (index rows `icon` and `tags`) — never into
entry.json, whose shape older OpenAR clients parse strictly.

    python3 scripts/listing.py <entry id>     # print the icon/tags it gets
"""

import json
import pathlib
import re
import sys

def _root() -> pathlib.Path:
    """icons.json is data: under `--root <dir>` (CI runs the base branch's
    scripts against a pull request's tree) it is read from that tree, so a PR
    may add the icon it uses; check_icons validates its shape."""
    if "--root" in sys.argv:
        index = sys.argv.index("--root")
        if index + 1 < len(sys.argv):
            return pathlib.Path(sys.argv[index + 1]).resolve()
    return pathlib.Path(__file__).resolve().parent.parent


ROOT = _root()
ICONS_PATH = ROOT / "icons.json"
TAG = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
MAX_TAGS = 12


def load_icons() -> dict:
    return json.loads(ICONS_PATH.read_text())


def read_listing(entry_dir: pathlib.Path) -> dict:
    path = entry_dir / "listing.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def tags_of(entry: dict, listing: dict) -> list[str]:
    seen: list[str] = []
    for tag in list(listing.get("tags", [])) + list(entry.get("categories", [])):
        tag = str(tag).strip().lower()
        if TAG.match(tag) and tag not in seen:
            seen.append(tag)
    return seen[:MAX_TAGS]


def pick_icon(entry: dict, listing: dict, icons: dict) -> str:
    """The listing's icon if it names one; else the highest-scoring icon:
    3 per category/tag it stands for, 1 per keyword found in the name and
    summary. Ties keep the library order; nothing matched → the default."""
    chosen = listing.get("icon")
    if isinstance(chosen, str) and chosen in icons["icons"]:
        return chosen
    tags = set(tags_of(entry, listing))
    text = f"{entry.get('name', '')} {entry.get('summary', '')} {entry.get('id', '')}".lower()
    best, best_score = icons["default"], 0
    for icon_id, icon in icons["icons"].items():
        score = 3 * len(tags & set(icon.get("categories", [])))
        score += sum(1 for word in icon.get("keywords", []) if re.search(rf"\b{re.escape(word)}\b", text))
        if score > best_score:
            best, best_score = icon_id, score
    return best


def listing_for(entry_dir: pathlib.Path, entry: dict, icons: dict | None = None) -> dict:
    icons = icons or load_icons()
    listing = read_listing(entry_dir)
    return {"icon": pick_icon(entry, listing, icons), "tags": tags_of(entry, listing)}


def check_listing(entry_dir: pathlib.Path, icons: dict) -> list[str]:
    """Problems with an entry's listing.json (empty when fine or absent)."""
    path = entry_dir / "listing.json"
    if not path.is_file():
        return []
    try:
        listing = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        return [f"listing.json is not valid JSON: {error}"]
    problems = []
    if not isinstance(listing, dict) or set(listing) - {"icon", "tags"}:
        problems.append("listing.json may only have `icon` and `tags`")
        return problems
    if "icon" in listing and listing["icon"] not in icons["icons"]:
        problems.append(f"listing icon {listing['icon']!r} is not in icons.json (add it there in the same PR)")
    tags = listing.get("tags", [])
    if not isinstance(tags, list) or len(tags) > MAX_TAGS or any(not isinstance(t, str) or not TAG.match(t) for t in tags):
        problems.append(f"listing tags must be up to {MAX_TAGS} lowercase words (a-z, 0-9, dashes, ≤32 chars)")
    return problems


def check_icons(icons: dict) -> list[str]:
    problems = []
    if icons.get("schemaVersion") != 1 or not isinstance(icons.get("icons"), dict):
        return ["icons.json must have schemaVersion 1 and an icons object"]
    if icons.get("default") not in icons["icons"]:
        problems.append("icons.json default must be one of its icons")
    for icon_id, icon in icons["icons"].items():
        if not TAG.match(icon_id):
            problems.append(f"icon id {icon_id!r} must be lowercase words")
        if not isinstance(icon.get("lucide"), str) or not re.fullmatch(r"[A-Z][A-Za-z0-9]+", icon["lucide"]):
            problems.append(f"icon {icon_id!r} needs a lucide component name (PascalCase)")
    return problems


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: scripts/listing.py <entry id>")
    entry_dir = ROOT / "entries" / "skills" / sys.argv[1]
    entry = json.loads((entry_dir / "entry.json").read_text())
    print(json.dumps(listing_for(entry_dir, entry), indent=2))


if __name__ == "__main__":
    main()
