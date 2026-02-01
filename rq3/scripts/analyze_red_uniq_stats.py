import glob
import re

total_remained_traces = 0
for filename in glob.glob("unique_traces_*"):
    with open(filename, "r") as f:
        for line in f:
            if "SPEC STATISTICS" in line:
                break
            if "remained=" in line:
                match = re.search(r"remained=(\d+)", line)
                if match:
                    total_remained_traces += int(match.group(1))

redundant_remained_list = []
unique_traces_preserved_sum = 0
in_redundant_section = False
in_preserved_section = False
preserved_lines_count = 0

with open("analyze_valg.log", "r") as f:
    for line in f:
        line = line.strip()
        if "Top 50: Redundant Traces (descending)" in line:
            in_redundant_section = True
            continue
        if "Top 50: Unique Traces - Preserved (descending)" in line:
            in_redundant_section = False
            in_preserved_section = True
            preserved_lines_count = 0
            continue

        if in_redundant_section and "Remained" in line:
            match = re.search(r"(\d+)\s+Remained", line)
            if match:
                redundant_remained_list.append(int(match.group(1)))

        if in_preserved_section and preserved_lines_count < 50:
            match = re.search(r"(\d+)\s+Unique Traces", line)
            if match:
                unique_traces_preserved_sum += int(match.group(1))
            preserved_lines_count += 1

redundant_total_remained = sum(redundant_remained_list)
print(f"Total remained in top 50 redundant traces: {redundant_total_remained}")
print(f"Total remained traces in unique traces files: {total_remained_traces}")
print(f"Ratio over all remained traces: {redundant_total_remained / total_remained_traces * 100:.2f}")

print(f"\nTotal unique traces in top 50 preserved: {unique_traces_preserved_sum}")
print(f"Ratio over all remained traces: {unique_traces_preserved_sum / 2016164 * 100:.2f}")
