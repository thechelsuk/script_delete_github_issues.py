# Delete GitHub Issues in BULK

A script to connect to the GitHub graphQL api to bulk delete closed GH issues

>  Deletion is **irreversible**. Always dry-run first.

## Requirements

- Python 3.7+
- `requests` — `pip install requests`
- A GitHub classic PAT (see below)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### 2. Create a classic PAT

Fine-grained PATs **do not support** issue deletion — a classic token is required.

1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Generate new token with scopes:
   - `repo` (full)
   - `delete_repo`
3. Copy the token immediately — it won't be shown again

### 3. Populate `config.py`

A `config.py` template is included in the repo — fill in your values:

```python
GH_OWNER = "your-org-or-username"
GH_REPO  = "your-repo-name"
GH_USER  = "your-github-username"
GH_PAT   = "ghp_xxxxxxxxxxxxxxxxxxxx"
```

> `config.py` is already in `.gitignore` — do not remove it from there or commit your credentials.

---

## Usage

**Dry run first — prints what would be deleted, no changes made:**

```bash
python delete_issues.py --dry-run
```

**Live run — prompts for confirmation before proceeding:**

```bash
python delete_issues.py
```

---

## Notes

- Only targets `CLOSED` issues — open issues are untouched
- Rate limiting is handled automatically
- Each deletion is logged with issue number and title
- `Ctrl+C` stops the script — any deletions already made cannot be undone
