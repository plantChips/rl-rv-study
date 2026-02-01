from pathlib import Path
import json
import math

def expand_series(tokens):
    series = []
    try:
        for tok in tokens:
            if 'x' in tok:
                v, n = tok.split('x')
                series.extend([int(v)] * int(n))
            else:
                series.append(int(tok))
    except Exception as e:
        print(f"Error in expand_series with tokens {tokens}: {e}", flush=True)
    return series

def parse_time_series_file(path):
    chunks = []
    current_chunk = {}
    last_loc = None
    try:
        with path.open() as f:
            for line in f:
                try:
                    line = line.rstrip()
                    if not line:
                        continue
                    if not line.startswith(" =>"):
                        loc = line
                        if last_loc and loc[0] < last_loc[0]:
                            chunks.append(current_chunk)
                            current_chunk = {}
                        current_chunk.setdefault(loc, [])
                        last_loc = loc
                    else:
                        content = line.strip()[4:-1]
                        tokens = [t.strip() for t in content.split(",")]
                        expanded = expand_series(tokens)
                        current_chunk[loc].append(expanded)
                except Exception as e_line:
                    print(f"Skipping line due to error: {e_line}", flush=True)
    except Exception as e_file:
        print(f"Error reading file {path}: {e_file}", flush=True)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def collect_hitmap_values(series_per_loc, num_indices=100):
    values = [0] * num_indices
    max_value = 0
    try:
        all_filtered_steps = []
        for series_group in series_per_loc:
            try:
                max_len = max(len(s) for s in series_group)
                filtered = [i for i in range(max_len) if any((i < len(s) and s[i] == 1) for s in series_group)]
                all_filtered_steps.append((series_group, filtered))
            except Exception as e_loc:
                print(f"Skipping a location due to error in collect_hitmap_values: {e_loc}", flush=True)
                continue

        current_index = 0
        total_filtered = 0
        for series_group, filtered in all_filtered_steps:
            total_filtered += len(filtered)
            for step in filtered:
                try:
                    consistent = all((step < len(s) and s[step] == 1) for s in series_group)
                    if consistent:
                        values[current_index] += 1
                    current_index = (current_index + 1) % num_indices
                except Exception as e_step:
                    print(f"Skipping step {step} due to error: {e_step}", flush=True)

        max_value = math.ceil(total_filtered / num_indices)
    except Exception as e_collect:
        print(f"Error in collect_hitmap_values: {e_collect}", flush=True)
    return values, max_value

def main():
    try:
        dirs = [Path(f"time-series-{i}") for i in (1, 2, 3)]
        try:
            projects = set(
                f.name.rsplit("_series", 1)[0]
                for f in dirs[0].glob("*_series")
                if all((d / f.name).exists() for d in dirs)
            )
        except Exception as e_proj:
            print(f"Error collecting projects: {e_proj}", flush=True)
            projects = set()

        out_data = {}

        for project in sorted(projects):
            try:
                chunk_maps = [parse_time_series_file(d / f"{project}_series") for d in dirs]
            except Exception as e_chunk:
                print(f"Skipping project {project} due to parse error: {e_chunk}", flush=True)
                continue

            if all(len(cm) == 1 for cm in chunk_maps):
                maps = [cm[0] for cm in chunk_maps]
                locs = set(maps[0].keys())
                series_per_loc = []

                for loc in locs:
                    try:
                        loc_series = [maps[i][loc][0] for i in range(3)]
                        series_per_loc.append(loc_series)
                    except Exception as e_loc:
                        print(f"Skipping location {loc} in project {project} due to error: {e_loc}", flush=True)
                        continue

                if series_per_loc:  # Only compute if there is at least one successful location
                    try:
                        values, max_value = collect_hitmap_values(series_per_loc)
                        out_data[project] = {"max": max_value, "values": values}
                        print(project, out_data[project], flush=True)
                    except Exception as e_collect:
                        print(f"Skipping project {project} due to hitmap error: {e_collect}", flush=True)
                        continue
                else:
                    print(f"No valid locations found for project {project}, skipping.", flush=True)
            else:
                print(f"Skipping project {project} due to unexpected chunk length", flush=True)

        try:
            with open("rq4_hitmap.json", "w") as f:
                json.dump(out_data, f, indent=2)
        except Exception as e_file:
            print(f"Error writing output JSON: {e_file}", flush=True)
    except Exception as e_main:
        print(f"Unexpected error in main: {e_main}", flush=True)

if __name__ == "__main__":
    main()

