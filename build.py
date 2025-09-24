import requests
import sys
import os
import json
import zipfile

GITHUB_API_URL = "https://api.github.com/search/repositories"
TAGS = [
    "unciv-mod-rulesets",
    "unciv-mod-expansions",
    "unciv-mod-graphics",
    "unciv-mod-audio",
    "unciv-mod-maps",
    "unciv-mod-fun",
    "unciv-mod-of-mods",
]

def fetch_repos_by_topic(topic, per_page=30):
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    else:
        print("Requires GITHUB_TOKEN https://github.com/settings/personal-access-tokens/new?name=Unciv-Mods-GitHub-Pages", file=sys.stderr)
        sys.exit(1)
    all_items = []
    page = 1
    while True:
        params = {
            "q": f"topic:{topic}",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }
        response = requests.get(GITHUB_API_URL, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch for topic {topic} page {page}: {response.status_code}", file=sys.stderr)
            break
        items = response.json().get("items", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < per_page:
            break
        page += 1
    return all_items


def build_markdown_table(repos):
    # Header
    rows = [
        "---",
        "hide:",
        "  - navigation",
        "  - toc",
        "---",
        "# Unciv Mods",
        "",
        "This is a list of mods available for [Unciv](https://yairm210.github.io/Unciv/).",
        "",
        "- [mods.json](assets/mods.json)",
        "- [mods.zip](assets/mods.zip)",
        "",
        "| Name | Author | Description | Stars |",
        "| ---- | ------ | ----------- | ----- |"
    ]

    # Write each entry
    for repo in repos:
        cleanname = repo['name'].replace("-", " ").replace("   ", " - ")
        name = f"[{cleanname}]({repo['html_url']})"
        desc = repo["description"] or ""
        desc = desc.replace("|", "\\|")
        author = f"[{repo.get('owner', {}).get('login')}]({repo['html_url']})"
        stars = repo["stargazers_count"]
        url = repo["html_url"]
        topics = ", ".join(repo.get("topics", []))
        row = f"| {name} | {author} | {desc} | {stars} |"
        rows.append(row)
    return "\n".join(rows)


def main():
    all_repos = {}
    for tag in TAGS:
        repos = fetch_repos_by_topic(tag, per_page=30)
        for repo in repos:
            all_repos[repo["id"]] = repo

    # index.md
    sorted_repos = sorted(all_repos.values(), key=lambda r: r["stargazers_count"], reverse=True)
    table = build_markdown_table(sorted_repos)
    with open("docs/index.md", "w", encoding="utf-8") as f:
        f.write(table)

    # mods.json
    minimal_repos = []
    for repo in sorted_repos:
        minimal_repos.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "author": repo.get("owner", {}).get("login"),
            "url": repo.get("html_url"),
            "stars": repo.get("stargazers_count"),
            "updated": repo.get("updated_at"),
            "topics": repo.get("topics", []),
        })
    mods_json_path = "docs/assets/mods.json"
    with open(mods_json_path, "w", encoding="utf-8") as jf:
        json.dump(minimal_repos, jf, ensure_ascii=False, indent=2)

    # Zip
    zip_path = "docs/assets/mods.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mods_json_path, arcname="mods.json")

    print("Wrote docs")

if __name__ == "__main__":
    main()
