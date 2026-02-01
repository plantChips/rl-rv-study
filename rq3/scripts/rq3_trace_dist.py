#!/usr/bin/env python3
import os
from pathlib import Path

def expand_series(tokens):
    series = []
    for tok in tokens:
        tok = tok.strip()
        if 'x' in tok:
            val, cnt = tok.split('x')
            val = int(val)
            cnt = int(cnt)
            series.extend([val] * cnt)
        else:
            series.append(int(tok))
    return series

def parse_time_series_file(ts_file):
    all_series = []
    current_series = []
    with open(ts_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('=>'):
                content = line[line.find('[')+1 : line.rfind(']')]
                tokens = [t.strip() for t in content.split(',')]
                current_series.extend(expand_series(tokens))
            elif " @ " in line:
                if current_series:
                    all_series.append(current_series)
                current_series = []
    if current_series:
        all_series.append(current_series)
    return all_series

def count_distances(series):
    distances = []
    last_one_idx = None
    for idx, val in enumerate(series):
        if val == 1:
            if last_one_idx is not None:
                dist = idx - last_one_idx
                distances.append(dist)
            last_one_idx = idx
    return distances

def classify_distances(distances):
    D1, Q1, Q2, Q3, Q4 = 0, 0, 0, 0, 0
    for d in distances:
        if d == 1:
            D1 += 1
        elif 1 < d <= 7.333275:
            Q1 += 1
        elif 7.333275 < d <= 72.1562:
            Q2 += 1
        elif 72.1562 < d <= 1371.5503:
            Q3 += 1
        elif d > 1371.5503:
            Q4 += 1
    return D1, Q1, Q2, Q3, Q4

def main():
    input_dir = Path('time-series-1')
    series_files = sorted([f for f in input_dir.glob('*_series') if f.is_file()])

    output_csv = Path('rq3_trace_dist.csv')
    with output_csv.open('w') as out_f:
        out_f.write("Project, Locations, D1-Pairs, Q1-Pairs, Q2-Pairs, Q3-Pairs, Q4-Pairs, Total-Pairs, Avg.Dist\n")
        for series_file in series_files:
            project_name = series_file.name.rsplit('_series', 1)[0]

            total_distances = 0
            sum_distances = 0
            D1_total, Q1_total, Q2_total, Q3_total, Q4_total = 0, 0, 0, 0, 0

            all_series = parse_time_series_file(series_file)
            num_locs = len(all_series)
            for series in all_series:
                distances = count_distances(series)
                total_distances += len(distances)
                sum_distances += sum(distances)

                D1, Q1, Q2, Q3, Q4 = classify_distances(distances)
                D1_total += D1
                Q1_total += Q1
                Q2_total += Q2
                Q3_total += Q3
                Q4_total += Q4

            avg_distance = (sum_distances / total_distances) if total_distances > 0 else 0

            out_f.write(
                f"{project_name}, {num_locs}, {D1_total}, {Q1_total}, {Q2_total}, {Q3_total}, {Q4_total}, {total_distances}, {avg_distance:.4f}\n"
            )
            out_f.flush()

if __name__ == "__main__":
    main()
