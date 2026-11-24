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
import time
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
    "c++": ("C++", "00599C", "cplusplus", "white"), "spring boot": ("Spring Boot", "6DB33F", "springboot", "white"),
    "next.js": ("Next.js", "000000", "nextdotjs", "white"), "react": ("React", "20232A", "react", "61DAFB"),
    "fastapi": ("FastAPI", "009688", "fastapi", "white"), "flask": ("Flask", "000000", "flask", "white"),
    "postgresql": ("PostgreSQL", "316192", "postgresql", "white"), "docker": ("Docker", "0DB7ED", "docker", "white"),
    "duckdb": ("DuckDB", "FFF000", "duckdb", "black"), "sqlite": ("SQLite", "003B57", "sqlite", "white"),
    "langchain": ("LangChain", "1C3C3C", "langchain", "white"), "ollama": ("Ollama", "000000", "ollama", "white"),
    "pandas": ("pandas", "150458", "pandas", "white"), "three.js": ("Three.js", "000000", "threedotjs", "white"),
    "node.js": ("Node.js", "339933", "nodedotjs", "white"), "mongodb": ("MongoDB", "47A248", "mongodb", "white"),
    "redis": ("Redis", "DC382D", "redis", "white"), "huggingface": ("Hugging Face", "FFD21E", "huggingface", "black"),
}


def fetch(url: str, api: bool = False):
    headers = {"User-Agent": "profile-readme"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    for attempt in range(4):                       # a slow or dropped response is retried, not fatal
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


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


NAMED_COLOURS = {"white": "#ffffff", "black": "#000000"}


def icon_path(slug: str) -> str:
    """The glyph's outline from the Simple Icons set (24x24), or "" if it can't be fetched (the badge is then text only)."""
    try:
        req = urllib.request.Request(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg", headers={"User-Agent": "profile-readme"})
        with urllib.request.urlopen(req, timeout=20) as r:
            m = re.search(r'\sd="([^"]+)"', r.read().decode("utf-8"))
            return m.group(1) if m else ""
    except Exception:
        return ""


def badge_file(key: str) -> str:
    """Draws one 'for the badge' badge as a standalone SVG in assets/badges/ and returns its README markdown.

    Hosting the badges in this repository (not on a third-party image service) means they can never fail to load."""
    label, colour, logo, logo_colour = BADGES[key]
    text = label.upper()
    background = f"#{colour}"
    light = sum(int(colour[i:i + 2], 16) * w for i, w in ((0, 0.299), (2, 0.587), (4, 0.114))) > 150
    text_fill = "#000000" if light else "#ffffff"
    glyph = icon_path(logo)
    text_x = 34 if glyph else 12
    text_w = round(len(text) * 9.4)
    width = text_x + text_w + 12
    logo_fill = NAMED_COLOURS.get(logo_colour, f"#{logo_colour}")
    glyph_svg = f'<path transform="translate(11,7) scale(0.5833)" fill="{logo_fill}" d="{glyph}"/>' if glyph else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-label="{label}">'
           f'<title>{label}</title><rect width="{width}" height="28" rx="3" fill="{background}"/>{glyph_svg}'
           f'<text x="{text_x}" y="18" fill="{text_fill}" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11" '
           f'font-weight="bold" textLength="{text_w}" lengthAdjust="spacing">{text}</text></svg>\n')
    folder = ROOT / "assets" / "badges"
    folder.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^a-z0-9]+", "-", key) + ".svg"
    (folder / name).write_text(svg, encoding="utf-8")
    return f"![{label}](assets/badges/{name})"


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

    # right now: whichever public project was pushed to most recently, with its latest commit message.
    # (The profile repo itself is skipped, otherwise this script's own commits would always win.)
    active = [r for r in repos if r["name"].lower() != OWNER.lower()]
    latest = max(active, key=lambda r: r["pushed_at"]) if active else None
    now_line = ""
    if latest:
        try:
            newest = fetch(f"https://api.github.com/repos/{OWNER}/{latest['name']}/commits?per_page=1", api=True)[0]
            message = short(newest["commit"]["message"].splitlines()[0], 90)
        except Exception:
            message = short(latest["description"], 90)
        when = dt.datetime.fromisoformat(latest["pushed_at"].replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M UTC")
        now_line = f"\nRight now: working in [`{latest['name']}`]({latest['html_url']}), latest commit: “{message}” ({when}).\n"

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
    for stale in (ROOT / "assets" / "badges").glob("*.svg"):      # drop badges for technologies no longer shown
        stale.unlink()
    tech = "\n" + " ".join(badge_file(k) for k in top) + "\n"

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
