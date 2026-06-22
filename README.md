# Delete GitHub Issues in BULK

A script to connect to the GitHub graphQL api to bulk delete closed GH issues

>  Deletion is **irreversible**. Always dry-run first.

## Requirements

- Python 3.7+
- `requests` library — `pip install requests`
- A GitHub classic PAT (see below)

## Setup

### 1. Clone / download the script

Place `delete_issues.py` and create `config.py` in the same directory.

### 2. Create a classic PAT

Fine-grained PATs **do not support** issue deletion — a classic token is required.

1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Generate new token with scopes:
   - `repo` (full)
   - `delete_repo`
3. Copy the token immediately — it won't be shown again

### 3. Create `config.py`

```python
GH_OWNER = "your-org-or-username"
GH_REPO  = "your-repo-name"
GH_USER  = "your-github-username"
GH_PAT   = "ghp_xxxxxxxxxxxxxxxxxxxx"
```

### 4. Add `config.py` to `.gitignore`

Create or append to `.gitignore` in the project root:

```
config.py
```

## Usage

**Dry run first — prints what would be deleted without making changes:**

```bash
python delete_issues.py --dry-run
```

**Live run — will prompt for confirmation before proceeding:**

```bash
python delete_issues.py
```

---

## Notes

- Only targets `CLOSED` issues — open issues are untouched
- Handles rate limiting automatically (sleeps and resumes if limit is approached)
- Logs each deletion with issue number and title
- Stop at any time with `Ctrl+C` — partial runs cannot be undone
