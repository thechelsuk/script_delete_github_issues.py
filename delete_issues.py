import datetime
import json
import time
import sys
import requests
import config

owner = config.GH_OWNER
repo  = config.GH_REPO
user  = config.GH_USER
tok   = config.GH_PAT

DRY_RUN = "--dry-run" in sys.argv


def info(r):
    return (int(r.headers['X-RateLimit-Remaining']),
            int(r.headers['X-RateLimit-Limit']))

def retryat(r):
    t = r.headers['X-RateLimit-Reset']
    return datetime.datetime.fromtimestamp(int(t)), int(t)

def req(q):
    dat = json.dumps({"query": q})
    return requests.post('https://api.github.com/graphql',
                         auth=(user, tok), data=dat)

def check_graphql_errors(r):
    """Return error message string if GraphQL errors present, else None."""
    body = r.json()
    if "errors" in body:
        return body["errors"]
    return None

def wait_for_rate_limit(r):
    remaining, _ = info(r)
    if remaining < 10:
        reset_dt, reset_ts = retryat(r)
        wait_secs = max(0, reset_ts - int(time.time())) + 5
        print(f'  Rate limit low ({remaining} remaining). Sleeping until {reset_dt} ({wait_secs}s)...')
        time.sleep(wait_secs)

def get_closed_issues(cursor=None):
    after = f', after: "{cursor}"' if cursor else ''
    q = """
    query {
      repository(owner: "%s", name: "%s") {
        issues(first: 20, states: [CLOSED]%s) {
          pageInfo { hasNextPage endCursor }
          edges {
            node { id number title }
          }
        }
      }
    }
    """ % (owner, repo, after)
    return req(q)

def delete_issue(iid):
    m = """
    mutation {
      deleteIssue(input: {issueId: "%s"}) {
        clientMutationId
      }
    }
    """ % iid
    return req(m)

def main():
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Targeting {owner}/{repo} — CLOSED issues only")

    if not DRY_RUN:
        confirm = input("Type 'yes' to confirm deletion of all closed issues: ")
        if confirm.strip().lower() != 'yes':
            print("Aborted.")
            return

    total_deleted = 0
    cursor = None

    while True:
        r0 = get_closed_issues(cursor)
        if r0.status_code != 200:
            print(f"HTTP error fetching issues: {r0.status_code}")
            print(r0.json())
            return

        errs = check_graphql_errors(r0)
        if errs:
            print(f"GraphQL error fetching issues: {errs}")
            return

        data     = r0.json()['data']['repository']['issues']
        lst      = data['edges']
        has_next = data['pageInfo']['hasNextPage']
        cursor   = data['pageInfo']['endCursor']

        rem, lim = info(r0)
        print(f"\nFetched {len(lst)} issues | API calls remaining: {rem}/{lim}")

        if not lst:
            print("No issues to delete.")
            break

        for item in lst:
            iid   = item['node']['id']
            num   = item['node']['number']
            title = item['node']['title'][:60]

            if DRY_RUN:
                print(f"  [DRY RUN] Would delete #{num}: {title}")
                total_deleted += 1
                continue

            r1 = delete_issue(iid)
            if r1.status_code != 200:
                print(f"  HTTP error deleting #{num}: {r1.status_code}")
                print(r1.json())
                return

            errs = check_graphql_errors(r1)
            if errs:
                print(f"  GraphQL error deleting #{num}: {errs}")
                return

            rem, lim = info(r1)
            print(f"  Deleted #{num}: {title} | {rem}/{lim} remaining")
            total_deleted += 1
            wait_for_rate_limit(r1)

        if not has_next:
            break

    print(f"\nDone. {'Would have deleted' if DRY_RUN else 'Deleted'} {total_deleted} issues.")

if __name__ == "__main__":
    main()
