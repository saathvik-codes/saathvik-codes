#!/usr/bin/env python3
"""
Keeps the profile README's look exactly as designed (banner, typing animation, badges, stat cards) while feeding the
parts that used to be typed by hand from live data:

  - Portfolio data (the profile.json both portfolio sites read): name, role line, flagship projects and their proof
    numbers, tags, social links, email.
  - GitHub API: live-site links (each repo's "homepage"), last push dates, language totals.

Only the text between the <!--NAME--> ... <!--/NAME--> markers in README.md is rewritten; everything else is untouched.
Run by .github/workflows/update-readme.yml daily, on demand, and when this file changes. Standard library only.
Locally:  GITHUB_TOKEN=$(gh auth token) python scripts/update_readme.py
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER = "saathvik-codes"
PORTFOLIO_REPO = "Portfolio-Showcase"
CONTENT_URL = f"https://raw.githubusercontent.com/{OWNER}/{PORTFOLIO_REPO}/portfolio-content/profile.json"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
NOW = dt.datetime.now(dt.timezone.utc)
MAX_BADGES = int(os.environ.get("MAX_BADGES", "16"))

# technology -> (label, hex colour, shields logo, logo colour). Anything not listed here is simply not badged.
BADGES = {
    "java": ("Java", "ED8B00", "openjdk", "white"), "go": ("Go", "00ADD8", "go", "white"),
    "python": ("Python", "3776AB", "python", "white"), "typescript": ("TypeScript", "3178C6", "typescript", "white"),
    "javascript": ("JavaScript", "F7DF1E", "javascript", "black"), "kotlin": ("Kotlin", "7F52FF", "kotlin", "white"),
    "c++": ("C++", "00599C", "cplusplus", "white"), "spring boot": ("Spring Boot", "6DB33F", "spring-boot", "white"),
    "next.js": ("Next.js", "000000", "next.js", "white"), "react": ("React", "20232A", "react", "61DAFB"),
    "fastapi": ("FastAPI", "009688", "fastapi", "white"), "flask": ("Flask", "000000", "flask", "white"),
    "postgresql": ("PostgreSQL", "316192", "postgresql", "white"), "docker": ("Docker", "0DB7ED", "docker", "white"),
    "duckdb": ("DuckDB", "FFF000", "duckdb", "black"), "sqlite": ("SQLite", "003B57", "sqlite", "white"),
    "langchain": ("LangChain", "1C3C3C", "langchain", "white"), "ollama": ("Ollama", "000000", "ollama", "white"),
    "pandas": ("pandas", "150458", "pandas", "white"), "three.js": ("Three.js", "000000", "three.js", "white"),
    "node.js": ("Node.js", "339933", "nodedotjs", "white"), "mongodb": ("MongoDB", "47A248", "mongodb", "white"),
    "redis": ("Redis", "DC382D", "redis", "white"), "huggingface": ("Hugging Face", "FFD21E", "huggingface", "black"),
}


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
    return pattern.sub(lambda m: f"{m.group(1)}{body}{m.group(2)}", text, count=1)


def norm(tag: str) -> str:
    return re.sub(r"\s*\d+(\.\d+)*$", "", tag.strip().lower())      # "Next.js 16" -> "next.js"


def badge(key: str) -> str:
    label, colour, logo, logo_colour = BADGES[key]
    return (f"![{label}](https://img.shields.io/badge/{urllib.parse.quote(label.replace('-', '--'))}-%23{colour}.svg"
            f"?style=for-the-badge&logo={logo}&logoColor={logo_colour})")


def repo_key(p: dict) -> str:
    return p["repo"].rstrip("/").split("/")[-1].lower()


def first_proof(p: dict) -> str:
    return next((s.strip() for s in (p.get("proofMetric") or "").split("·") if s.strip() and not s.strip().lower().startswith("live")), "")


def main() -> None:
    content = fetch(CONTENT_URL)
    profile = content["profile"]
    repos = [r for r in fetch(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner", api=True)
             if not r["fork"] and not r["archived"]]
    by_name = {r["name"].lower(): r for r in repos}
    flagships = content["flagshipProjects"]

    # banner: name and role line
    desc = f"{profile['headlineRole']} | {profile['subRole'].split('·')[0].strip()}"
    banner = ("\n  <img src=\"https://capsule-render.vercel.app/api?type=waving&color=0:0EA5E9,100:38BDF8&height=180&section=header"
              f"&text={urllib.parse.quote(profile['name'], safe='')}&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=38"
              f"&desc={urllib.parse.quote(desc, safe='')}&descAlignY=58&descSize=18\" />\n")

    # typing animation: one line per flagship project, from its own proof number
    lines = [short(f"{p['title']}: {first_proof(p)}", 52) for p in flagships]
    typing = ("\n  <img src=\"https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&color=38BDF8"
              "&center=true&vCenter=true&width=600&lines=" + ";".join(urllib.parse.quote_plus(l) for l in lines) + "\" />\n")

    # right now: the flagship project pushed to most recently
    flagship_repos = [by_name[repo_key(p)] for p in flagships if repo_key(p) in by_name]
    latest = max(flagship_repos, key=lambda r: r["pushed_at"]) if flagship_repos else None
    now_line = (f"Right now: [`{latest['name']}`]({latest['html_url']}): {short(latest['description'], 120)} "
                f"(last push {ago(latest['pushed_at'])})." if latest else "")

    # socials: the same three badges as always, with live values
    linkedin = next((s["href"] for s in content["socialLinks"] if "linkedin" in s["href"]), "")
    portfolio = by_name.get(PORTFOLIO_REPO.lower(), {}).get("homepage") or ""
    socials = (f"\n[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)]({linkedin}) "
               f"[![email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:{profile['email']}) "
               f"[![Portfolio](https://img.shields.io/badge/Portfolio-000000?logo=vercel&logoColor=white)]({portfolio})\n")

    # tech stack: your own skills list is the main signal; language usage on GitHub and project tags add evidence
    ALIASES = {"c / c++": "c++", "sqlite wal": "sqlite", "huggingface": "huggingface", "dockerfile": "docker"}
    score: Counter = Counter()
    for group in content.get("skillMatrix", []):
        for position, item in enumerate(re.split(r"\s*·\s*", group["items"])):
            key = ALIASES.get(norm(item), norm(item))
            if key in BADGES:
                score[key] += 4 + max(0, 3 - position)      # listing a skill earlier in its group signals emphasis
    totals: Counter = Counter()      # bytes of code per language
    presence: Counter = Counter()    # number of repos using each language ("Dockerfile" counts as Docker)
    for r in repos:
        if r["size"]:
            try:
                langs = fetch(r["languages_url"], api=True)
            except Exception:
                continue
            totals.update(langs)
            presence.update(ALIASES.get(norm(l), norm(l)) for l in langs)
    for lang, _ in totals.most_common(10):
        if ALIASES.get(norm(lang), norm(lang)) in BADGES:
            score[ALIASES.get(norm(lang), norm(lang))] += 3
    for key, repos_using in presence.items():
        if key in BADGES:
            score[key] += min(repos_using, 3)
    # repository descriptions that name a technology ("Spring Boot 3 / Java 21 ...") count too, up to three repos each
    descriptions = " | ".join((r["description"] or "").lower() for r in repos).split(" | ")
    for key, (label, *_rest) in BADGES.items():
        mentions = sum(1 for d in descriptions if label.lower() in d)
        score[key] += min(mentions, 3)
    for weight, group in ((2, flagships), (1, content.get("archiveProjects", []))):
        for p in group:
            for t in p.get("tags", []):
                if ALIASES.get(norm(t), norm(t)) in BADGES:
                    score[ALIASES.get(norm(t), norm(t))] += weight
    top = [k for k, _ in score.most_common(MAX_BADGES)]
    tech = "\n" + " ".join(badge(k) for k in top) + "\n"

    # projects: the portfolio's flagship list, with the live link from each repo's homepage
    projects = []
    for p in flagships:
        repo = by_name.get(repo_key(p))
        proof = " · ".join(s.strip() for s in (p.get("proofMetric") or "").split("·") if s.strip() and not s.strip().lower().startswith("live"))
        live = f" [Live site]({repo['homepage']})." if repo and repo.get("homepage") else ""
        projects.append(f"**[{p['title']}]({p['repo']})** — {proof}.{live}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, body in (("BANNER", banner), ("TYPING", typing), ("NOW", now_line), ("SOCIALS", socials), ("TECH", tech),
                       ("PROJECTS", "\n\n" + "\n\n".join(projects) + "\n\n")):
        readme = fill(readme, name, body)
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"updated: {len(projects)} projects, {len(lines)} typing lines; badges: {', '.join(BADGES[k][0] for k in top)}")


if __name__ == "__main__":
    main()
