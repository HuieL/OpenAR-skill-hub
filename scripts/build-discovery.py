#!/usr/bin/env python3
"""Generate community/discovery.json (New / Recently Updated / Trending).

- New: the date each entry was first recorded in this registry (the first
  commit that added its entry.json), from this repository's git history.
- Recently Updated: the last commit that touched the entry directory.
- Trending: public GitHub signals (stars, forks, last push) for the
  distinct source repositories, snapshotted at generation time. Stars are
  a GitHub-activity signal, not an OpenAR install count or a quality
  rating; the metric and window are recorded in the file itself.

Every network fetch must succeed; on any failure the script exits nonzero
without writing, so the previous discovery.json is kept.

Skills are read from this repository. When --extensions <path> points at
a checkout of OpenAR-extension-hub, its entries are included too and
referenced as extension:<id>.

An optional GITHUB_TOKEN environment variable is used for API rate limits
only; no token is required, written, or logged.
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
COMMUNITY = ROOT / "community"
GITHUB_API = "https://api.github.com"


def git(args):
    return subprocess.run(
        ["git"] + args, cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def first_recorded(entry_rel):
    out = git(["log", "--diff-filter=A", "--format=%cI", "--", entry_rel])
    dates = [line for line in out.splitlines() if line.strip()]
    return dates[-1] if dates else None


def last_recorded(entry_dir):
    out = git(["log", "-1", "--format=%cI", "--", entry_dir])
    return out.strip() or None


def read_entries(repo_dir, kind):
    rows = []
    entries_dir = repo_dir / "entries" / "skills" if kind == "skill" else repo_dir / "entries" / "extension"
    if not entries_dir.is_dir():
        return rows
    for entry_path in sorted(entries_dir.glob("*/entry.json")):
        entry = json.loads(entry_path.read_text())
        rows.append((entry_path, entry, kind))
    return rows


def github_repo_stats(repo, token):
    url = f"{GITHUB_API}/repos/{repo}"
    headers = {"User-Agent": "OpenAR-skill-hub-discovery", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read())
    return {
        "repo": repo,
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "pushedAt": data["pushed_at"],
    }


def build(extension_hub, token):
    rows = read_entries(ROOT, "skill")
    if extension_hub is not None and (extension_hub / "entries").is_dir():
        rows += read_entries(extension_hub, "extension")

    new, updated, by_repo = [], [], {}
    for entry_path, entry, kind in rows:
        ref = f"{kind}:{entry['id']}"
        first = first_recorded(entry_path)
        last = last_recorded(entry_path)
        if first:
            new.append({"id": ref, "firstRecorded": first})
        if last:
            updated.append({"id": ref, "lastRecorded": last})
        repo = entry.get("source", {}).get("repo")
        if repo and repo.startswith("http"):
            parts = [p for p in repo.rstrip("/").split("/") if p]
            if "github.com" in parts:
                parts = parts[parts.index("github.com") + 1:]
            repo = "/".join(parts[:2]) if len(parts) >= 2 else None
        if repo and "/" in repo:
            by_repo.setdefault(repo, []).append(ref)
        upstream_repo = entry.get("upstream", {}).get("repo")
        if upstream_repo and "/" in upstream_repo and upstream_repo != repo:
            by_repo.setdefault(upstream_repo, []).append(ref)

    trending_repos = []
    for repo in sorted(by_repo):
        stats = github_repo_stats(repo, token)
        stats["entries"] = sorted(by_repo[repo])
        trending_repos.append(stats)
    trending_repos.sort(key=lambda r: (-r["stars"], r["repo"]))

    new.sort(key=lambda r: r["firstRecorded"], reverse=True)
    updated.sort(key=lambda r: r["lastRecorded"], reverse=True)

    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skillHub": git(["rev-parse", "HEAD"]).strip(),
        "new": new,
        "updated": updated,
        "trending": {
            "metric": "github-stars",
            "window": "all-time snapshot",
            "note": "GitHub stars are not OpenAR install counts and not a quality rating.",
            "repos": trending_repos,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extensions", type=pathlib.Path, default=None,
                        help="optional checkout of OpenAR-extension-hub")
    parser.add_argument("--check", action="store_true",
                        help="verify the committed discovery.json is current")
    args = parser.parse_args()

    projection = build(args.extensions, os.environ.get("GITHUB_TOKEN"))
    rendered = json.dumps(projection, indent=2, ensure_ascii=False) + "\n"
    path = COMMUNITY / "discovery.json"
    if args.check:
        current = json.loads(path.read_text()) if path.exists() else {}
        same = current.get("skillHub") == projection["skillHub"] and current.get("new") == projection["new"]
        if not same:
            sys.exit("community/discovery.json is stale; run scripts/build-discovery.py and commit it")
        print("discovery.json is current")
        return
    path.write_text(rendered)
    print(f"wrote community/discovery.json ({len(projection['new'])} new, "
          f"{len(projection['updated'])} updated, {len(projection['trending']['repos'])} trending repos)")


if __name__ == "__main__":
    main()
