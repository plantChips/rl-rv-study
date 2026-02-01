#!/usr/bin/env python3

import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
TOP_K = 50

LINE_RE = re.compile(
    r"^(?P<spec>.+?) @ (?P<loc>.+?): "
    r"(?P<unique>\d+) Unique Traces, "
    r"(?P<redundant>\d+) Redundant Traces, "
    r"(?P<preserved>\d+) Preserved, "
    r"(?P<remained>\d+) Remained$"
)

EXCLUDED_PROJECTS = {"CoreNLP", "json-rules", "orientdb-etl", "simplexml"}

def collect_entries():
    entries = []

    for name in os.listdir(BASE_DIR):
        if not name.startswith("rq3-"):
            continue

        project = name[len("rq3-"):]
        if project in EXCLUDED_PROJECTS:
            continue

        project_dir = os.path.join(BASE_DIR, name)

        if not os.path.isdir(project_dir):
            continue

        for fname in os.listdir(project_dir):
            if not fname.endswith(".txt"):
                continue

            fpath = os.path.join(project_dir, fname)

            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    m = LINE_RE.match(line)
                    if not m:
                        continue

                    unique = int(m.group("unique"))
                    preserved = int(m.group("preserved"))
                    remained = int(m.group("remained"))

                    entries.append({
                        "project": project,
                        "line": line,
                        "remained": remained,
                        "unique_minus_preserved": unique - preserved,
                    })
    return entries

def print_top(entries, key, title):
    print(f"\n==== Top {TOP_K}: {title} ====\n")

    for e in sorted(entries, key=lambda x: x[key], reverse=True)[:TOP_K]:
        print(f"[{e['project']}] {e['line']}")

def main():
    entries = collect_entries()

    print_top(
        entries,
        key="remained",
        title="Redundant Traces (descending)"
    )

    print_top(
        entries,
        key="unique_minus_preserved",
        title="Unique Traces - Preserved (descending)"
    )

if __name__ == "__main__":
    main()
