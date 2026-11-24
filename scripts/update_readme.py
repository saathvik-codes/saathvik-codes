#!/usr/bin/env python3
"""
Rebuilds the marked sections of README.md from live sources, so nothing about projects, links or stats is typed by hand.

  - Portfolio data (the same profile.json both portfolio sites read): role line, flagship projects with their one-line
    proof, social links, email.
  - GitHub API: each project's live demo link (the repo "homepage"), last push date, and language totals.

Run by .github/workflows/update.yml every day, on demand, and whenever this script changes. Standard library only.
Locally:  GITHUB_TOKEN=$(gh auth token) python scripts/update_readme.py
"""
import datetime as dt
import json
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER = "saathvik-codes"
PROFILE_REPO = OWNER                      # the special repo whose README is the profile page
PORTFOLIO_REPO = "Portfolio-Showcase"
CONTENT_URL = f"https://raw.githubusercontent.com/{OWNER}/{PORTFOLIO_REPO}/portfolio-content/profile.json"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
NOW = dt.datetime.now(dt.timezone.utc)
# One calm palette for the language bar (readable on GitHub's light and dark themes)
COLOURS = ["#b4532a", "#2f6b66", "#c9962b", "#7a3114", "#cf8a5f", "#9c3b2e", "#5e5548", "#a8a091"]


def fetch(url: str, api: bool = False):
    headers = {"User-Agent": "profile-readme"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def ago(iso: str) -> str:
    days = (NOW - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 60:
        return f"{days} days ago"
    return f"{days // 30} months ago"


def short(text: str, limit: int) -> str:
    """Trim to a whole word, with an ellipsis, so nothing is cut mid-word."""
    text = (text or "").strip().rstrip(".")
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:—- ") + "…"


def fill(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!--{name}-->).*?(<!--/{name}-->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"README.md is missing the <!--{name}--> markers")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text, count=1)


def language_svg(totals: Counter) -> str:
    top = totals.most_common(8)
    total = sum(v for _, v in top) or 1
    width, bar_y, x = 720, 8, 0.0
    parts, legend = [], []
    for i, (lang, n) in enumerate(top):
        w = n / total * width
        parts.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w - 2, 1):.1f}" height="12" rx="2" fill="{COLOURS[i]}"/>')
        x += w
        col, row = i % 4, i // 4
        lx, ly = col * 180, 44 + row * 24
        legend.append(f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{COLOURS[i]}"/>'
                      f'<text x="{lx + 18}" y="{ly}" font-size="13" fill="#768390">{lang} <tspan fill="#9aa4ae">{n / total:.0%}</tspan></text>')
    height = 44 + ((len(top) - 1) // 4) * 24 + 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" role="img" aria-label="Language share across public repositories">'
            + "".join(parts) + "".join(legend) + "</svg>\n")


def main() -> None:
    content = fetch(CONTENT_URL)
    profile = content["profile"]
    repos = [r for r in fetch(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner", api=True)
             if not r["fork"] and not r["archived"]]
    by_name = {r["name"].lower(): r for r in repos}

    # --- projects: the portfolio's flagship list, enriched with live links and push dates from GitHub
    lines, flagship_repos = [], []
    for p in content["flagshipProjects"]:
        repo = by_name.get(p["repo"].rstrip("/").split("/")[-1].lower())
        proof = " · ".join(s.strip() for s in (p.get("proofMetric") or "").split("·") if s.strip() and not s.strip().lower().startswith("live"))
        live = f" [Live site]({repo['homepage']})." if repo and repo.get("homepage") else ""
        lines.append(f"**[{p['title']}]({p['repo']})**: {proof}.{live}")
        if repo:
            flagship_repos.append(repo)

    # --- "right now": the flagship project pushed to most recently
    now_repo = max(flagship_repos, key=lambda r: r["pushed_at"]) if flagship_repos else None
    now_line = (f"**Right now:** [{now_repo['name']}]({now_repo['html_url']}): {short(now_repo['description'], 110)} (last push {ago(now_repo['pushed_at'])})"
                if now_repo else "")

    # --- recent activity: the latest pushes across all public repos
    recent = sorted((r for r in repos if r["name"] != PROFILE_REPO), key=lambda r: r["pushed_at"], reverse=True)[:6]
    activity = [f"- [{r['name']}]({r['html_url']}): {short(r['description'], 90)} ({ago(r['pushed_at'])})" for r in recent]

    # --- languages across public repos (own work only)
    totals: Counter = Counter()
    for r in repos:
        if r["size"] == 0:
            continue
        try:
            totals.update(fetch(r["languages_url"], api=True))
        except Exception:
            pass
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "languages.svg").write_text(language_svg(totals), encoding="utf-8")

    # --- links
    portfolio = by_name.get(PORTFOLIO_REPO.lower(), {}).get("homepage") or ""
    links = ([f"[Portfolio]({portfolio})"] if portfolio else []) + [f"[{s['label']}]({s['href']})" for s in content["socialLinks"]
                                                                       if "instagram" not in s["href"]]
    links.append(f"[Email](mailto:{profile['email']})")

    live_count = sum(1 for r in repos if r.get("homepage"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme = fill(readme, "HEADLINE", f"{profile['headlineRole']} · {profile['subRole']} · {profile['location']}")
    readme = fill(readme, "NOW", now_line)
    readme = fill(readme, "PROJECTS", "\n\n".join(lines))
    readme = fill(readme, "ACTIVITY", "\n".join(activity))
    readme = fill(readme, "LINKS", " · ".join(links))
    readme = fill(readme, "STATS", f"{len(repos)} public repositories · {live_count} with a live site · {profile['leetcodeSolved']}+ LeetCode problems solved")
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"updated: {len(lines)} projects, {len(recent)} recent, {len(totals)} languages")


if __name__ == "__main__":
    main()
