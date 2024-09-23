
from pathlib import Path
import shutil
import subprocess as sp
import os
import csv

curr_file = Path(__file__).resolve()
curr_dir = curr_file.parent
root_dir = curr_dir.parent.parent

subject_name = "opencv_dnn"

stat_dir = root_dir / "statistics" / subject_name
out_dir = root_dir / "out" / subject_name

mbfl_features_rank_stats_csv = stat_dir / "mbfl_features-rank-stats.csv"

removing_list = []

with open(mbfl_features_rank_stats_csv, 'r') as f:
    reader = csv.reader(f)
    # read columns of header
    next(reader)
    for row in reader:
        version_name = row[0]
        # 14: rank of buggy function (function level) (met)
        # 18: rank of buggy function (function level) (muse)
        met_rank = int(row[14])
        muse_rank = int(row[18])
        # print(f"{version_name}: {met_rank}, {muse_rank}")

        if met_rank == 1094 and muse_rank == 1094:
            removing_list.append((version_name, met_rank, muse_rank))

import random
random.shuffle(removing_list)
print(f"Total removing versions: {len(removing_list)}")

mbfl_removed_dir = out_dir / "mbfl_features_removed_30"

limit = 30
for version_name, met_rank, muse_rank in removing_list[:limit]:
    print(f"Removing {version_name} (met: {met_rank}, muse: {muse_rank})")
    version_dir = mbfl_removed_dir / version_name
    assert version_dir.exists()

    # remove the directory
    shutil.rmtree(version_dir)
