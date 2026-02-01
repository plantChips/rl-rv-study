import os
import re
import math
import optuna
import random
import json
import time
import logging

logging.getLogger("optuna").setLevel(logging.WARNING)

DEFAULT_THRESHOLD = 0.0001
INIT_C = 5.0
INIT_N = 0.0

TIME_SERIES_DIR = "time-series-1"
OUTPUT_DIR = "results-run-1"

def expand_token(tok):
    if "x" in tok:
        val, cnt = tok.split("x")
        return [int(val)] * int(cnt)
    return [int(tok)]

def parse_locations(file_path):
    locations = {}
    current_loc = None

    header_re = re.compile(r"^(.*?) @ (.*?:\d+)")
    series_re = re.compile(r"\[(.*)\]")

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            m = header_re.match(line)
            if m:
                current_loc = m.group(1) + " @ " + m.group(2)
                locations.setdefault(current_loc, [])
                continue

            if line.startswith("=>") and current_loc:
                m = series_re.search(line)
                if not m:
                    continue
                tokens = [t.strip() for t in m.group(1).split(",")]
                series = []
                for t in tokens:
                    series.extend(expand_token(t))
                locations[current_loc].append(series)

    return locations

def decide_action(Qc, Qn, alpha, epsilon, time_step):
    if time_step == 0:
        return INIT_N <= INIT_C
    if random.random() < epsilon:
        return random.choice([True, False])
    return Qn <= Qc

def simulate_series(series, alpha, epsilon):
    Qc, Qn = INIT_C, INIT_N
    num_tot = num_uniq = num_dup = 0
    converged = False
    converged_action = None

    for t, true_action in enumerate(series):
        if converged:
            if converged_action:
                num_tot += 1
                num_uniq += (true_action == 1)
                num_dup += (true_action == 0)
            continue

        action = decide_action(Qc, Qn, alpha, epsilon, t)

        if action:
            num_tot += 1
            num_uniq += (true_action == 1)
            num_dup += (true_action == 0)
            reward = 1.0 if true_action == 1 else 0.0
            Qc += alpha * (reward - Qc)
        else:
            reward = (num_dup / num_tot) if num_tot > 0 else 0.0
            Qn += alpha * (reward - Qn)

        if abs(1.0 - abs(Qc - Qn)) < DEFAULT_THRESHOLD:
            converged = True
            converged_action = Qn <= Qc

    return num_uniq, num_dup

def tune_hyperparams(series_list, n_trials=100):
    trial_results = []

    def objective(trial):
        alpha = round(trial.suggest_float("alpha", 0.01, 0.99, step=0.01), 2)
        epsilon = round(trial.suggest_float("epsilon", 0.01, 0.99, step=0.01), 2)

        total_uniq = 0
        total_dup = 0
        for s in series_list:
            u, d = simulate_series(s, alpha, epsilon)
            total_uniq += u
            total_dup += d

        trial_results.append((alpha, epsilon, total_uniq, total_dup))
        return total_uniq

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    best_unique = max(r[2] for r in trial_results)
    best_trials = [r for r in trial_results if r[2] == best_unique]

    alpha, epsilon, _, _ = min(best_trials, key=lambda r: r[3])
    return alpha, epsilon

def main():
    project_files = [
        f for f in os.listdir(TIME_SERIES_DIR)
        if f.endswith("_series")
    ]
    total_projects = len(project_files)

    for idx, fname in enumerate(project_files, start=1):
        project_name = fname.replace("_series", "")
        series_file = os.path.join(TIME_SERIES_DIR, fname)

        print(
            f"\n --> Processing {project_name}: ({idx}/{total_projects})",
            flush=True
        )

        locations = parse_locations(series_file)

        csv_path = os.path.join(OUTPUT_DIR, f"{project_name}.csv")
        csv_rows = []

        proj_total_u = proj_total_d = 0
        proj_def_u = proj_def_d = 0
        print("Loc,Total,Default", flush=True)

        for idx, (loc, series_list) in enumerate(locations.items(), 1):
            start = time.time()

            total_u = total_d = 0
            def_u = def_d = 0

            for s in series_list:
                total_u += sum(s)
                total_d += len(s) - sum(s)
                u, d = simulate_series(s, 0.9, 0.1)
                def_u += u
                def_d += d

            proj_total_u += total_u
            proj_total_d += total_d
            proj_def_u += def_u
            proj_def_d += def_d
            
            row = [
                loc,
                f"{total_u}({total_d})",
                f"{def_u}({def_d})"
                # f"{tuned_u}({tuned_d})"
            ]

            elapsed = time.time() - start
            print(f"[{idx}/{len(locations)}] {loc} (time: {elapsed:.2f}s)", flush=True)
            print(",".join(row), flush=True)

            csv_rows.append(row)

        with open(csv_path, "w") as f:
            # f.write("Loc,Total,Default,Default(tuned)\n")
            f.write("Loc,Total,Default\n")
            for r in csv_rows:
                f.write(",".join(r) + "\n")
            f.write(
                f"__TOTAL__,"
                f"{proj_total_u}({proj_total_d}),"
                f"{proj_def_u}({proj_def_d})\n"
                # f"{proj_tuned_u}({proj_tuned_d})\n"
            )

        print(
            f"\nProject summary for {project_name}: "
            f"Total={proj_total_u}({proj_total_d}), "
            f"Default={proj_def_u}({proj_def_d})",
            # f"Tuned={proj_tuned_u}({proj_tuned_d})",
            flush=True
        )
        print(f"Saved results to {csv_path}", flush=True)

if __name__ == "__main__":
    main()
