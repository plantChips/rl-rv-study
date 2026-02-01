#!/usr/bin/env python3
import os, re, tarfile, csv

def count_violations_from_tar(tar_path):
    if not os.path.isfile(tar_path):
        return 0
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            for m in tar:
                if m.isfile() and m.name.endswith("/project/violation-counts"):
                    f = tar.extractfile(m)
                    if f is None:
                        return 0
                    return sum(1 for _ in f.read().decode("utf-8", errors="ignore").splitlines())
    except:
        return 0
    return 0

def count_unique_traces(tar_path):
    if not os.path.isfile(tar_path):
        return 0
    total = 0
    pattern = re.compile(r'/all-traces[^/]*/unique-traces\.txt$')
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            for m in tar:
                if m.isfile() and pattern.search(m.name):
                    f = tar.extractfile(m)
                    if f is not None:
                        lines = list(f)
                        total += max(0, len(lines)-1)
        return total
    except:
        return 0

def read_duration_nth(file_path, n=1):
    if not os.path.isfile(file_path):
        return 0
    try:
        count = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("Duration:"):
                    count += 1
                    if count == n:
                        parts = line.split()
                        if len(parts) >= 2:
                            return int(parts[1])
    except:
        return 0
    return 0

output_csv = "rq5.csv"
valg_ducb_dir = "results-valg-ducb"
projects = sorted([fname[:-len("-valgj.txt")] for fname in os.listdir(valg_ducb_dir) if fname.endswith("-valgj.txt")])

header1 = ["Project","ValgJ","","ValgJ (DUCB)","","ValgJ (DSTS)","","ValgT","","ValgT (DUCB)","","ValgT (DSTS)",""]
header2 = ["", "time","violation","time","violation","time","violation","time","unique_traces","time","unique_traces","time","unique_traces"]

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header1)
    writer.writerow(header2)
    for project in projects:
        print(f"Processing {project}...")
        files_time = {
            "valgj": f"results-valg-rq5/{project}-valgj.txt",
            "valgt": f"results-valg-rq5/{project}-valgt.txt",
            "valgj-ducb": f"results-valg-ducb/{project}-valgj.txt",
            "valgt-ducb": f"results-valg-ducb/{project}-valgt.txt",
            "valgj-dsts": f"results-valg-dsts/{project}-valgj.txt",
            "valgt-dsts": f"results-valg-dsts/{project}-valgt.txt",
        }

        t_valgj = read_duration_nth(files_time["valgj"], n=1)
        t_valgt = read_duration_nth(files_time["valgt"], n=1)
        t_valgj_ducb = read_duration_nth(files_time["valgj-ducb"], n=1)
        t_valgt_ducb = read_duration_nth(files_time["valgt-ducb"], n=1)
        t_valgj_dsts = read_duration_nth(files_time["valgj-dsts"], n=1)
        t_valgt_dsts = read_duration_nth(files_time["valgt-dsts"], n=1)

        files_count = {
            "valgj": f"outputs-valg-rq5/output-{project}-valgj.tar.gz",
            "valgt": f"outputs-valg-rq5/output-{project}-valgt.tar.gz",
            "valgj-ducb": f"outputs-valg-ducb/output-{project}-valgj.tar.gz",
            "valgt-ducb": f"outputs-valg-ducb/output-{project}-valgt.tar.gz",
            "valgj-dsts": f"outputs-valg-dsts/output-{project}-valgj.tar.gz",
            "valgt-dsts": f"outputs-valg-dsts/output-{project}-valgt.tar.gz",
        }

        violation_valgj = count_violations_from_tar(files_count["valgj"])
        uniq_valgt = count_unique_traces(files_count["valgt"])
        violation_valgj_ducb = count_violations_from_tar(files_count["valgj-ducb"])
        uniq_valgt_ducb = count_unique_traces(files_count["valgt-ducb"])
        violation_valgj_dsts = count_violations_from_tar(files_count["valgj-dsts"])
        uniq_valgt_dsts = count_unique_traces(files_count["valgt-dsts"])

        row = [
            project,
            t_valgj, violation_valgj,
            t_valgj_ducb, violation_valgj_ducb,
            t_valgj_dsts, violation_valgj_dsts,
            t_valgt, uniq_valgt,
            t_valgt_ducb, uniq_valgt_ducb,
            t_valgt_dsts, uniq_valgt_dsts
        ]
        writer.writerow(row)

print(f"Finished! CSV saved as {output_csv}")
