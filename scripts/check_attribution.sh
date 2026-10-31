#!/usr/bin/env bash
# CI attribution check (job attribution in .github/workflows/ci.yml, IMD-61, specification §13.7).
#
# Inputs (environment):
#   GITHUB_EVENT_PATH  pull_request event payload; base and head come from pull_request.base.sha and
#                      pull_request.head.sha, never from HEAD (GitHub's synthetic merge commit), and
#                      the body from pull_request.body.
#   TEAM_EMAILS        repository variable: the ten team emails, separated by commas (spaces,
#                      semicolons and new lines also work); compared without regard to case.
# Needs the full history (actions/checkout with fetch-depth: 0) and python3 (reads the payload).
#
# For every commit of git rev-list --no-merges <base>..<head> it fails when
#   team-email  the author email is not in TEAM_EMAILS,
#   committer   the committer (name and email) differs from the author,
#   message     the message breaks a rule of .githooks/commit-msg (run as is, so the rules are the same);
# and it fails when the pull-request body breaks a rule of .githooks/commit-msg.
# Commits on main after Rebase and merge carry GitHub's committer and are not checked (pull_request only).
# Exit 0: all checks pass; 1: at least one rule failed; 2: the inputs are missing or unusable.
# Emails are never printed; each failure names the commit and the rule.

set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
hook="$repo_root/.githooks/commit-msg"

setup_error() {
  echo "attribution: ERROR $*" >&2
  exit 2
}

event="${GITHUB_EVENT_PATH:-}"
[ -n "$event" ] && [ -f "$event" ] || setup_error "GITHUB_EVENT_PATH must name a pull_request event payload file"
[ -f "$hook" ] || setup_error "$hook is missing"

# payload_field <dotted path>: prints the field of the event payload, or nothing when it is absent or null.
payload_field() {
  python3 -I -c 'import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
for key in sys.argv[2].split("."):
    value = value.get(key) if isinstance(value, dict) else None
sys.stdout.write("" if value is None else str(value))' "$event" "$1"
}

base=$(payload_field pull_request.base.sha)
head=$(payload_field pull_request.head.sha)
[ -n "$base" ] && [ -n "$head" ] || setup_error "the payload has no pull_request.base.sha or pull_request.head.sha"

team=$(printf '%s' "${TEAM_EMAILS:-}" | tr '[:upper:]' '[:lower:]' | tr -s ',; \t\r' '\n' | sed '/^$/d')
[ -n "$team" ] || setup_error "TEAM_EMAILS is empty; set the repository variable TEAM_EMAILS (comma-separated)"

git cat-file -e "${base}^{commit}" 2>/dev/null || setup_error "base commit ${base:0:7} is not in the clone (use fetch-depth: 0)"
git cat-file -e "${head}^{commit}" 2>/dev/null || setup_error "head commit ${head:0:7} is not in the clone (use fetch-depth: 0)"

commits=$(git rev-list --no-merges --reverse "${base}..${head}")
[ -n "$commits" ] || setup_error "no commits between base ${base:0:7} and head ${head:0:7}"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

failures=0
checked=0
report() {
  echo "attribution: FAIL $*"
  failures=$((failures + 1))
}

for commit in $commits; do
  checked=$((checked + 1))
  short=$(git rev-parse --short "$commit")
  author_email=$(git log -1 --format='%ae' "$commit" | tr '[:upper:]' '[:lower:]')
  author=$(git log -1 --format='%an' "$commit")
  committer=$(git log -1 --format='%cn' "$commit")
  committer_email=$(git log -1 --format='%ce' "$commit" | tr '[:upper:]' '[:lower:]')

  if ! printf '%s\n' "$team" | grep -Fxq -- "$author_email"; then
    report "commit $short rule team-email failed: the author email is not in TEAM_EMAILS"
  fi
  if [ "$author" != "$committer" ] || [ "$author_email" != "$committer_email" ]; then
    report "commit $short rule committer failed: the committer differs from the author (author and commit as the part owner)"
  fi
  git log -1 --format='%B' "$commit" >"$tmp/message"
  if ! hook_output=$(sh "$hook" "$tmp/message" 2>&1); then
    report "commit $short ${hook_output#commit-msg: }"
  fi
done

payload_field pull_request.body >"$tmp/body"
if ! hook_output=$(sh "$hook" "$tmp/body" 2>&1); then
  report "pull request body ${hook_output#commit-msg: }"
fi

if [ "$failures" -gt 0 ]; then
  echo "attribution: FAIL $failures problem(s) in $checked commit(s) of ${base:0:7}..${head:0:7} and the pull request body"
  exit 1
fi
echo "attribution: PASS $checked commit(s) of ${base:0:7}..${head:0:7} and the pull request body"
