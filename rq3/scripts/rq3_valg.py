#!/usr/bin/env python3

import os
import re
import shutil
import tarfile

INPUT_DIR = "outputs-valg-rq3"
RESULTS_DIR = "results-valg-rq3"

def parse_time_series(ts_file):
    ts_dict = {}
    with open(ts_file) as f:
        last_loc = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            if '@' in line and '=>' not in line:
                last_loc = line
                continue
            if '=>' in line and last_loc:
                seq = line.split('=>', 1)[1].strip()
                seq = seq[1:-1]
                ts_vals = []
                for item in seq.split(','):
                    item = item.strip()
                    if 'x' in item:
                        v, n = item.split('x')
                        ts_vals.extend([int(v)] * int(n))
                    else:
                        ts_vals.append(int(item))
                ts_dict[last_loc.replace('Monitor', '')] = ts_vals
                last_loc = None
    return ts_dict

def parse_trajectory(traj_file):
    traj_dict = {}
    loc_count = {}
    with open(traj_file) as f:
        last_loc = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            if '@' in line and '=>' not in line:
                last_loc = line
                continue
            if '=>' in line and last_loc:
                actions_list = re.findall(r'<(\d+): A=([^,]+),', line)
                traj_dict[last_loc] = {
                    "actions": actions_list,
                    "converged": "[converged]" in line
                }
                loc_count[last_loc] = loc_count.get(last_loc, 0) + 1
                last_loc = None
    traj_dict = {k: v for k, v in traj_dict.items() if loc_count[k] == 1}
    return traj_dict

def process_pair(ts_file, traj_file, out_file):
    ts_dict = parse_time_series(ts_file)
    traj_dict = parse_trajectory(traj_file)

    with open(out_file, 'w') as out:
        for loc, traj_info in traj_dict.items():
            actions_list = traj_info["actions"]
            converged = traj_info["converged"]
            ts_vals = ts_dict.get(loc, [])
            stepped = 0
            redundant = 0
            last_action = actions_list[-1][1] if actions_list else None

            for idx_str, act in actions_list:
                idx = int(idx_str)
                if idx >= len(ts_vals):
                    continue
                val = ts_vals[idx]
                if act == 'create':
                    if val == 1:
                        stepped += 1
                    else:
                        redundant += 1

            if converged and last_action == 'create':
                for idx in range(len(actions_list), len(ts_vals)):
                    val = ts_vals[idx]
                    if val == 1:
                        stepped += 1
                    else:
                        redundant += 1

            uniq = sum(1 for v in ts_vals if v == 1)
            red = sum(1 for v in ts_vals if v == 0)
            out.write(
                f"{loc}: {uniq} Unique Traces, {red} Redundant Traces, "
                f"{stepped} Preserved, {redundant} Remained \n"
            )

def untar_selected_dirs(tar_path, dirs_to_extract, extract_path):
    with tarfile.open(tar_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if any(m.name.startswith(d) for d in dirs_to_extract)]
        tar.extractall(path=extract_path, members=members)

def main():
    for fname in os.listdir(INPUT_DIR):
        if not fname.startswith("output-") or not fname.endswith(".tar.gz"):
            continue

        project_name = fname[len("output-"):-len(".tar.gz")]
        if not "simplexml" in project_name:
            continue
        tar_path = os.path.join(INPUT_DIR, fname)
        project_dir = os.path.join(INPUT_DIR, f"output-{project_name}")

        ts_dir = os.path.join(project_dir, "time-series")
        traj_dir = os.path.join(project_dir, "trajectories")

        untar_selected_dirs(
            tar_path,
            [f"output-{project_name}/time-series", f"output-{project_name}/trajectories"],
            INPUT_DIR
        )

        if not os.path.isdir(ts_dir) or not os.path.isdir(traj_dir):
            continue

        out_project_dir = os.path.join(RESULTS_DIR, f"rq3-{project_name}")
        os.makedirs(out_project_dir, exist_ok=True)

        ts_files = {}
        traj_files = {}

        for f in os.listdir(ts_dir):
            if f.startswith("time-series-"):
                ts_files[f[len("time-series-"):]] = os.path.join(ts_dir, f)

        for f in os.listdir(traj_dir):
            if f.startswith("trajectories-"):
                traj_files[f[len("trajectories-"):]] = os.path.join(traj_dir, f)

        for id_, ts_file in ts_files.items():
            traj_file = traj_files.get(id_)
            if not traj_file:
                continue
            out_file = os.path.join(out_project_dir, f"{id_}.txt")
            process_pair(ts_file, traj_file, out_file)

        if os.path.isdir(project_dir):
            shutil.rmtree(project_dir)

if __name__ == "__main__":
    main()
