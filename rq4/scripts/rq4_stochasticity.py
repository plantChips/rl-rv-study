#!/usr/bin/env python3

import csv
import re
from pathlib import Path

VAL_RE = re.compile(r"(\d+)\((\d+)\)")

def parse_val(s):
    m = VAL_RE.fullmatch(s.strip())
    if not m:
        raise ValueError(f"Malformed value: {s}")
    return int(m.group(1)), int(m.group(2))


def read_project_csv(path):
    base_uniq = 0
    base_red = 0
    per_loc = {}

    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            if not row:
                continue

            loc = row[0].strip()

            if loc == "__TOTAL__":
                continue

            total_uniq, total_red = parse_val(row[1])
            def_uniq, def_red = parse_val(row[2])

            base_uniq += total_uniq
            base_red += total_red
            per_loc[loc] = (def_uniq, def_red)

    return base_uniq, base_red, per_loc


tuning_dirs = [
    Path("results-run-1"),
    Path("results-run-2"),
    Path("results-run-3"),
]

projects = sorted(p.stem for p in tuning_dirs[0].glob("*.csv"))

with open("rq4_stochasticity.csv", "w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow([
        "project",
        "baseUniq",
        "baseRed",
        "minSumUniq",
        "maxSumUniq",
        "minSumRed",
        "maxSumRed",
    ])

    for project in projects:
        base_uniq = 0
        base_red = 0
        loc_values = {}

        for i, d in enumerate(tuning_dirs):
            csv_path = d / f"{project}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(csv_path)

            buniq, bred, per_loc = read_project_csv(csv_path)

            if i == 0:
                base_uniq = buniq
                base_red = bred

            for loc, vals in per_loc.items():
                loc_values.setdefault(loc, []).append(vals)

        min_sum_uniq = 0
        max_sum_uniq = 0
        min_sum_red = 0
        max_sum_red = 0

        for loc, vals in loc_values.items():
            uniqs = [u for u, r in vals]
            reds = [r for u, r in vals]

            min_sum_uniq += min(uniqs)
            max_sum_uniq += max(uniqs)
            min_sum_red += min(reds)
            max_sum_red += max(reds)

        writer.writerow([
            project,
            base_uniq,
            base_red,
            min_sum_uniq,
            max_sum_uniq,
            min_sum_red,
            max_sum_red,
        ])
