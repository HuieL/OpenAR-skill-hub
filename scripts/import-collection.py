#!/usr/bin/env python3
"""Import a whole skill collection (one upstream repository) as hub entries.

    python3 scripts/import-collection.py collections/<name>.json [--checkout <dir>]

The collection file names the repository, the 40-hex commit every entry is
pinned to, the id prefix, the license and author, the skills to leave out
(each with its reason), the categories of each skill and optional display
names (`names`, else the folder name title-cased). Every skill folder
under `skillsPath` becomes entries/skills/<prefix>.<folder>/ with an
entry.json (manifest with sha256 pins, made the same way as add-entry.py)
and a listing.json (tags; the icon is picked by scripts/listing.py). The
skill files stay upstream. A skill that is neither listed nor excluded
stops the import, so a new upstream skill is a conscious decision.

Re-running with a new `revision` re-pins every entry; entries of excluded
or vanished skills are removed. Then the generated files are rebuilt and the
validator runs. Nothing is pushed.
"""

import argparse
import re
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("add_entry", ROOT / "scripts" / "add-entry.py")
add_entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(add_entry)
sys.path.insert(0, str(ROOT / "scripts"))
import listing as listing_mod  # noqa: E402


def die(message: str) -> None:
    sys.exit(f"import-collection: {message}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("collection")
    ap.add_argument("--checkout", help="an existing clone of the repository (it is checked at the pinned commit)")
    args = ap.parse_args()
    cfg = json.loads(pathlib.Path(args.collection).read_text())
    repo, revision, prefix = cfg["repo"], cfg["revision"], cfg["idPrefix"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        die("revision must be a 40-hex commit")
    # The prefix becomes the first segment of every id and the pruning glob:
    # a plain lowercase word, never a reserved namespace or another
    # collection's / a hand-added entry's prefix.
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,31}", prefix) or prefix in ("ora", "openra", "hub"):
        die(f"idPrefix {prefix!r} must be a lowercase word (not ora, openra or hub)")
    for other in sorted((ROOT / "collections").glob("*.json")):
        if other.resolve() != pathlib.Path(args.collection).resolve() and json.loads(other.read_text()).get("idPrefix") == prefix:
            die(f"idPrefix {prefix!r} is already used by {other.name}")
    sections, skills, exclude = cfg["sections"], cfg["skills"], cfg.get("exclude", {})
    for name in sorted(skills):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
            die(f"skill folder {name!r} cannot be an id segment")
    # Pruning removes <prefix>.* entries: none of them may come from elsewhere.
    for existing in sorted((ROOT / "entries" / "skills").glob(f"{prefix}.*/entry.json")):
        if json.loads(existing.read_text())["source"]["repo"].lower() != repo.lower():
            die(f"{existing.parent.name} uses the {prefix!r} prefix but is not from {repo}")
    icons = listing_mod.load_icons()

    with tempfile.TemporaryDirectory(prefix="hub-collection-") as tmp:
        if args.checkout:
            checkout_dir = pathlib.Path(args.checkout).resolve()
            head = add_entry.git("rev-parse", "HEAD", cwd=checkout_dir)
            if head != revision:
                die(f"{checkout_dir} is at {head[:12]}, the collection pins {revision[:12]}")
            if add_entry.git("status", "--porcelain", cwd=checkout_dir):
                die(f"{checkout_dir} has local changes")
        else:
            checkout_dir = pathlib.Path(tmp) / "src"
            add_entry.checkout(repo, revision, checkout_dir)
        base = checkout_dir / cfg.get("skillsPath", "")
        found = {d.name: d for d in add_entry.find_skills(base)}
        unknown = sorted(set(found) - set(skills) - set(exclude))
        if unknown:
            die(f"skills neither listed nor excluded in {args.collection}: {', '.join(unknown)}")
        license_file = next((n for n in add_entry.LICENSE_NAMES if (checkout_dir / n).is_file()), None)
        if not license_file:
            die(f"{repo} has no LICENSE file at its root")

        written = []
        for name in sorted(skills):
            if name in exclude:
                die(f"{name} is both listed and excluded")
            if name not in found:
                die(f"{name} is listed but has no SKILL.md at {revision[:12]}")
            skill_dir = found[name]
            fm = add_entry.frontmatter(skill_dir / "SKILL.md")
            if not fm.get("name") or not fm.get("description"):
                die(f"{name}: SKILL.md frontmatter needs both name and description")
            files = add_entry.manifest(skill_dir)
            slugs = []
            for section in skills[name]:
                if section not in sections:
                    die(f"{name}: unknown section {section!r}")
                slugs += [s for s in sections[section] if s not in slugs]
            entry_id = f"{prefix}.{name}"
            author = cfg["author"]
            entry = {
                "schemaVersion": 1,
                "id": entry_id,
                "kind": "skill",
                "name": cfg.get("names", {}).get(name, fm["name"].replace("-", " ").title())[:64],
                "summary": " ".join(fm["description"].split())[:1000],
                "authors": [{"name": author["name"], **({"github": author["github"]} if author.get("github") else {})}],
                **({"registrySubmitter": cfg["submitter"]} if cfg.get("submitter") else {}),
                # The first slug of each section is the category; the rest are tags.
                "categories": [sections[s][0] for s in skills[name]],
                "source": {"repo": repo, "path": skill_dir.relative_to(checkout_dir).as_posix(), "revision": revision},
                "version": cfg.get("version") or revision,
                "license": cfg["license"],
                "licenseFile": "LICENSE",
                "review": {"status": "unreviewed", "reviewedRevision": None, "reviewer": None},
                "compat": {},
                "delivery": "hub",
                "files": files,
                "totalBytes": sum(f["bytes"] for f in files),
                "requires": [],
                "permissionsNote": add_entry.DEFAULT_PERMISSIONS_NOTE,
            }
            entry_dir = ROOT / "entries" / "skills" / entry_id
            entry_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checkout_dir / license_file, entry_dir / "LICENSE")
            (entry_dir / "entry.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
            tags = [t for t in slugs + cfg.get("tags", []) if t not in entry["categories"]][: listing_mod.MAX_TAGS]
            draft = {"tags": tags}
            listing = {"icon": listing_mod.pick_icon(entry, draft, icons), "tags": tags}
            (entry_dir / "listing.json").write_text(json.dumps(listing, indent=2) + "\n")
            written.append(entry_id)

        # Entries of this collection that are no longer listed go away.
        keep = set(written)
        for old in sorted((ROOT / "entries" / "skills").glob(f"{prefix}.*")):
            if old.name not in keep:
                shutil.rmtree(old)
                print(f"removed {old.name}")

    print(f"{len(written)} entries from {repo}@{revision[:12]}; {len(exclude)} excluded", flush=True)
    for script in ("build-index.py", "build-community.py", "validate.py"):
        if subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT).returncode != 0:
            die(f"{script} failed")


if __name__ == "__main__":
    main()
