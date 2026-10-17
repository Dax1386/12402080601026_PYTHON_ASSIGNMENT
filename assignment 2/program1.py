"""Q1: Stream a text file and summarize unique valid emails by domain."""
import re
import sys
from collections import defaultdict
from pathlib import Path

EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._+-])[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.(?:com|edu|org)(?![A-Za-z0-9.-])", re.I)

def extract_emails(path):
    users_by_domain = defaultdict(set)
    with open(path, "r", encoding="utf-8", errors="replace") as source:
        for line in source:
            for match in EMAIL_RE.finditer(line):
                email = match.group().lower()
                local, domain = email.rsplit("@", 1)
                # Reject malformed dot placement and empty domain labels.
                labels = domain.split(".")
                if (not local or local.startswith(".") or local.endswith(".") or ".." in local
                        or any(not label for label in labels) or len(labels) < 2):
                    continue
                users_by_domain[domain].add(email)
    return users_by_domain

def main():
    try:
        path = input("Text file path: ").strip()
        if not path or not Path(path).is_file():
            raise ValueError("Please provide the path to an existing text file.")
        for domain, emails in sorted(extract_emails(path).items()):
            print(domain, len(emails), min(emails))
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
