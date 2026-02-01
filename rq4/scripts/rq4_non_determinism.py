from pathlib import Path
from itertools import product, permutations

def expand_series(tokens):
    series = []
    for tok in tokens:
        if 'x' in tok:
            v, n = tok.split('x')
            series.extend([int(v)] * int(n))
        else:
            series.append(int(tok))
    return series

def parse_time_series_file(path):
    chunks = []
    current_chunk = {}
    last_loc = None

    with path.open() as f:
        for line in f:
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

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def compare_series(series_group):
    max_len = max(len(s) for s in series_group)
    diverging = 0
    total = 0

    for i in range(max_len):
        vals = []
        for s in series_group:
            if i < len(s):
                vals.append(s[i])
        if all(v == 0 for v in vals):
            continue
        total += 1
        if len(vals) < len(series_group) or not all(v == vals[0] for v in vals):
            diverging += 1

    return diverging, total

def main():
    dirs = [Path(f"time-series-{i}") for i in (1, 2, 3)]
    out = Path("rq4_non_determinism.csv")

    out.write_text("Project,divergingLocs,totalLocs,divergingSteps,totalSteps\n")

    projects = set(
        f.name.rsplit("_series", 1)[0]
        for f in dirs[0].glob("*_series")
        if all((d / f.name).exists() for d in dirs)
    )

    for project in sorted(projects):
        chunk_maps = [
            parse_time_series_file(d / f"{project}_series")
            for d in dirs
        ]

        diverging_locs = 0
        total_locs = 0
        diverging_steps = 0
        total_steps = 0

        if all(len(cm) == 1 for cm in chunk_maps):
            maps = [cm[0] for cm in chunk_maps]

            loc_sets = [set(m.keys()) for m in maps]
            union_locs = set.union(*loc_sets)
            common_locs = set.intersection(*loc_sets)

            total_locs += len(union_locs)
            diverging_locs += len(union_locs - common_locs)

            for loc in common_locs:
                for series_group in product(
                    maps[0][loc], maps[1][loc], maps[2][loc]
                ):
                    d, t = compare_series(series_group)
                    diverging_steps += d
                    total_steps += t
                    break

        else:
            used = [set() for _ in range(3)]
            print(f"[{project}] Num. of chunks: {len(chunk_maps[0])}, {len(chunk_maps[1])}, {len(chunk_maps[2])}")

            for i, m1 in enumerate(chunk_maps[0]):
                for j, m2 in enumerate(chunk_maps[1]):
                    for k, m3 in enumerate(chunk_maps[2]):
                        if j in used[1] or k in used[2]:
                            continue

                        if set(m1.keys()) == set(m2.keys()) == set(m3.keys()):
                            used[0].add(i)
                            used[1].add(j)
                            used[2].add(k)

                            locs = set(m1.keys())
                            total_locs += len(locs)

                            for loc in locs:
                                for series_group in product(
                                    m1[loc], m2[loc], m3[loc]
                                ):
                                    d, t = compare_series(series_group)
                                    diverging_steps += d
                                    total_steps += t
                                    break

            """
            rem = [
                [m for idx, m in enumerate(cm) if idx not in used[x]]
                for x, cm in enumerate(chunk_maps)
            ]

            if rem[0]:
                n = min(len(rem[0]), len(rem[1]), len(rem[2]))
                best = None
                print(f"[{project}] Mismatched chunks: {len(rem[0])}, {len(rem[1])}, {len(rem[2])}", flush=True)

                for perm2 in permutations(range(len(rem[1]))):
                    for perm3 in permutations(range(len(rem[2]))):
                        d_locs = 0
                        t_locs = 0
                        d_steps = 0
                        t_steps = 0

                        for i in range(n):
                            m1 = rem[0][i]
                            m2 = rem[1][perm2[i]]
                            m3 = rem[2][perm3[i]]

                            loc_sets = [set(m1.keys()), set(m2.keys()), set(m3.keys())]
                            union_locs = set.union(*loc_sets)
                            common_locs = set.intersection(*loc_sets)

                            t_locs += len(union_locs)
                            d_locs += len(union_locs - common_locs)

                            for loc in common_locs:
                                for series_group in product(
                                    m1[loc], m2[loc], m3[loc]
                                ):
                                    d, t = compare_series(series_group)
                                    d_steps += d
                                    t_steps += t
                                    break

                        score = (d_locs, d_steps)
                        if best is None or score < best[0]:
                            best = (score, t_locs, d_steps, t_steps)

                if best:
                    diverging_locs += best[0][0]
                    total_locs += best[1]
                    diverging_steps += best[2]
                    total_steps += best[3]
            """

        with out.open("a") as f:
            f.write(
                f"{project},{diverging_locs},{total_locs},"
                f"{diverging_steps},{total_steps}\n"
            )

if __name__ == "__main__":
    main()
