#!/usr/bin/env python3
"""Generate community/creators.json from the registry entries.

creators.json is a rebuildable projection, like skills.json: one row per
creator (keyed by GitHub login when one is recorded, otherwise by name),
listing every entry they are credited on and the roles they hold there.
Original author, maintainer, contributor, adapter and registry submitter
are recorded as separate roles; submitting or adapting is not authorship.

Skills are read from entries/skills/*/entry.json in this repository. When
--extensions <path> points at a checkout of OpenAR-extension-hub, its
entries are read too and referenced as extension:<id>; otherwise the
projection covers skills only and records extensionHub: null.

Run with --check to verify the committed file is current without writing.
"""

import argparse
import json
import pathlib
import subprocess
import sys

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
COMMUNITY = ROOT / "community"

ROLE_FIELDS = (
    ("authors", "author"),
    ("maintainers", "maintainer"),
    ("contributors", "contributor"),
    ("adapters", "adapter"),
    ("registrySubmitter", "submitter"),
)


def git_head():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return None


def read_entries(repo_dir: pathlib.Path, kind: str):
    rows = []
    entries_dir = repo_dir / "entries" / kind if kind == "extension" else repo_dir / "entries" / "skills"
    if not entries_dir.is_dir():
        return rows
    for entry_path in sorted(entries_dir.glob("*/entry.json")):
        entry = json.loads(entry_path.read_text())
        rows.append((f"{kind}:{entry['id']}", entry))
    return rows


def collect(rows):
    creators = {}
    for ref, entry in rows:
        for field, role in ROLE_FIELDS:
            value = entry.get(field)
            if field == "registrySubmitter":
                value = [value] if value else []
            if not isinstance(value, list):
                continue
            for item in value:
                if field == "authors":
                    if not isinstance(item, dict) or not item.get("name"):
                        continue
                    key = item.get("github") or f"name:{item['name']}"
                    row = creators.setdefault(
                        key, {"github": item.get("github"), "name": item["name"], "credits": []}
                    )
                    if row.get("name") != item["name"] and not row.get("github"):
                        row["name"] = item["name"]
                else:
                    if not isinstance(item, str):
                        continue
                    key = item
                    row = creators.setdefault(key, {"github": item, "name": None, "credits": []})
                credit = next((c for c in row["credits"] if c["entry"] == ref), None)
                if credit is None:
                    credit = {"entry": ref, "roles": []}
                    row["credits"].append(credit)
                if role not in credit["roles"]:
                    credit["roles"].append(role)
    for row in creators.values():
        row["credits"].sort(key=lambda c: c["entry"])
    return [creators[k] for k in sorted(creators)]


def build(extension_hub):
    rows = read_entries(ROOT, "skill")
    ext_revision = None
    if extension_hub is not None and (extension_hub / "entries").is_dir():
        rows += read_entries(extension_hub, "extension")
        try:
            ext_revision = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=extension_hub, capture_output=True, text=True, check=True
            ).stdout.strip()
        except subprocess.CalledProcessError:
            ext_revision = None
    return {
        "schemaVersion": 1,
        "skillHub": git_head(),
        "extensionHub": ext_revision,
        "creators": collect(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extensions", type=pathlib.Path, default=None,
                        help="optional checkout of OpenAR-extension-hub")
    parser.add_argument("--root", type=pathlib.Path, default=None,
                        help="registry tree to read (resolved at import; see _root)")
    parser.add_argument("--check", action="store_true",
                        help="verify the committed creators.json is current")
    args = parser.parse_args()

    projection = build(args.extensions)
    rendered = json.dumps(projection, indent=2, ensure_ascii=False) + "\n"
    path = COMMUNITY / "creators.json"
    if args.check:
        current = path.read_text() if path.exists() else ""
        try:
            committed = json.loads(current) if current else {}
        except json.JSONDecodeError:
            committed = {}
        # The provenance pins (skillHub/extensionHub) name the commit the
        # file was generated at; a committed snapshot can never pin its own
        # containing commit, so only the projection itself is compared.
        comparable = {"schemaVersion": projection["schemaVersion"],
                      "creators": projection["creators"]}
        if {k: committed.get(k) for k in comparable} != comparable:
            sys.exit("community/creators.json is stale; run scripts/build-community.py and commit it")
        print(f"creators.json is current ({len(projection['creators'])} creators)")
        return
    path.write_text(rendered)
    print(f"wrote community/creators.json ({len(projection['creators'])} creators)")


if __name__ == "__main__":
    main()
