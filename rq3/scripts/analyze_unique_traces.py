#!/usr/bin/env python3

import os
import re
from collections import defaultdict, Counter

BASE_DIR = ".."
PROJECT_PREFIX = "rq3-"

LINE_RE = re.compile(
    r"^(?P<spec>.+?)\s*@\s*(?P<file>[^:]+:\d+):\s*"
    r"(?P<uniq>\d+)\s+Unique Traces,\s*"
    r"(?P<redundant>\d+)\s+Redundant Traces,\s*"
    r"(?P<preserved>\d+)\s+Preserved,\s*"
    r"(?P<remained>\d+)\s+Remained"
)

unique_map = defaultdict(list)
spec_statistics = defaultdict(Counter)
total_locations = 0
total_unique_traces = 0

def iter_projects():
    for name in os.listdir(BASE_DIR):
        if name.startswith(PROJECT_PREFIX):
            yield name[len(PROJECT_PREFIX):], os.path.join(BASE_DIR, name)

for project, project_dir in iter_projects():
    if not os.path.isdir(project_dir):
        continue

    if "simplexml" in project:
        continue

    for fname in os.listdir(project_dir):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(project_dir, fname)

        with open(path, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or "Unique Traces" not in line:
                    continue

                m = LINE_RE.match(line)
                if not m:
                    continue

                spec = m.group("spec")
                file_loc = m.group("file")
                uniq = int(m.group("uniq"))
                redundant = int(m.group("redundant"))
                if uniq == 0:
                    continue
                remained = int(m.group("remained"))

                location = f"[{project}] {spec} @ {file_loc}"

                entry = {
                    "location": location,
                    "spec": spec,
                    "remained": remained,
                    "redundant": redundant,
                    "uniq_actual": uniq
                }

                if uniq > 100:
                    unique_map[101].append(entry)
                else:
                    unique_map[uniq].append(entry)

                spec_statistics[spec][uniq] += 1
                total_locations += 1
                total_unique_traces += uniq

print("Unique traces distribution:")
print("--------------------------------")

for uniq in sorted(unique_map.keys()):
    if uniq <= 100:
        count = len(unique_map[uniq])
        percent = (count / total_locations) * 100
        print(f"{uniq}: {count} ({percent:.2f}%)")
    else:
        actual_counts = Counter(e["uniq_actual"] for e in unique_map[uniq])
        for actual_uniq in sorted(actual_counts.keys()):
            count = actual_counts[actual_uniq]
            percent = (count / total_locations) * 100
            print(f"{actual_uniq}: {count} ({percent:.2f}%)")

print("--------------------------------")
print(f"Total locations: {total_locations}")
print(f"Total unique traces: {total_unique_traces}")
print("--------------------------------")

for uniq, entries in unique_map.items():
    filename = f"unique_traces_{uniq}" if uniq <= 100 else "unique_traces_100_above"

    if uniq <= 100:
        entries.sort(key=lambda x: x["remained"], reverse=True)
        spec_counter = Counter(e["spec"] for e in entries)

        with open(filename, "w") as out:
            for e in entries:
                out.write(f"{e['location']} | remained={e['remained']} (out of {e['redundant']})\n")

            out.write("\n=== SPEC STATISTICS ===\n")
            for spec, count in spec_counter.most_common():
                out.write(f"{spec}: {count}\n")
    else:
        entries_by_uniq = defaultdict(list)
        for e in entries:
            entries_by_uniq[e["uniq_actual"]].append(e)

        with open(filename, "w") as out:
            for actual_uniq in sorted(entries_by_uniq.keys()):
                out.write(f"\n=== Unique Traces {actual_uniq} ===\n")
                group = entries_by_uniq[actual_uniq]
                group.sort(key=lambda x: x["remained"], reverse=True)
                for e in group:
                    out.write(f"{e['location']} | remained={e['remained']} (out of {e['redundant']})\n")

            spec_counter = Counter(e["spec"] for e in entries)
            out.write("\n=== SPEC STATISTICS ===\n")
            for spec, count in spec_counter.most_common():
                out.write(f"{spec}: {count}\n")


with open("spec_statistics", "w") as out:
    for spec in sorted(spec_statistics.keys()):
        out.write(f"{spec}\n")
        total_spec_locations = sum(spec_statistics[spec].values())
        for uniq in sorted(spec_statistics[spec].keys()):
            count = spec_statistics[spec][uniq]
            percent = (count / total_spec_locations) * 100
            out.write(f"{uniq}: {count} ({percent:.2f}%)\n")
        out.write("\n")
