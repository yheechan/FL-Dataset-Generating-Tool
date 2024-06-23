#!/usr/bin/python3

import sys
from pathlib import Path
import subprocess as sp
import argparse
import csv
import math

def return_parser():
    parser = argparse.ArgumentParser(description='Measure Metallaxis and Muse suspiciouness scores and writes to susp_score.csv file')
    parser.add_argument(
        "-f", "--feature-file",
        help="Enter absolute path to the fault localization feature file (CSV)",
        required=True,
        default=None
    )
    
    return parser


def get_prerequite_data(feature_file):
    totFailed_cnt = -1
    max_mutant_count = -1
    with open(feature_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            totFailed_cnt = int(row['# of totfailed_TCs'])
            max_mutant_count = int(row['# of mutants'])
            break
    
    assert totFailed_cnt != -1, "Error: totFailed_cnt is not set"
    assert max_mutant_count != -1, "Error: max_mutant_count is not set"


    return totFailed_cnt, max_mutant_count


def get_mutant_feature_name_pairs(max_mutant_count):
    mutant_feature_name_pairs = []
    for i in range(1, max_mutant_count+1):
        mutant_feature_name_pairs.append((f'm{i}:f2p', f'm{i}:p2f'))
    return mutant_feature_name_pairs

def get_total_killed_count(feature_file, mutant_feature_name_pairs):
    total_f2p = 0
    total_p2f = 0

    with open(feature_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            for f2p_name, p2f_name in mutant_feature_name_pairs:
                f2p = int(row[f2p_name])
                p2f = int(row[p2f_name])

                if f2p == -1:
                    assert p2f == -1
                    continue
                if p2f == -1:
                    assert f2p == -1
                    continue

                total_f2p += f2p
                total_p2f += p2f
    
    return total_f2p, total_p2f


def measure_metallaxis(row, mutant_feature_name_pairs):
    total_failing_tc_count = int(row['# of totfailed_TCs'])

    met_score_list = []
    # per mutant
    cnt = 0
    for f2p_m, p2f_m in mutant_feature_name_pairs:
        cnt += 1
        f2p = int(row[f2p_m])
        p2f = int(row[p2f_m])

        if f2p == -1:
            assert p2f == -1, f'{p2f} != -1'
            continue
        if p2f == -1:
            assert f2p == -1, f'{f2p} != -1'
            continue

        score = 0.0
        if f2p + p2f == 0:
            score = 0.0
        else:
            score = ((f2p) / math.sqrt(total_failing_tc_count * (f2p + p2f)))

        met_score_list.append(score)

    if len(met_score_list) == 0:
        return 0.0

    final_met_score = max(met_score_list)
    return final_met_score

def measure_muse(row, total_f2p, total_p2f, mutant_feature_name_pairs):
    utilized_mutant_cnt = 0
    line_total_f2p = 0
    line_total_p2f = 0

    final_muse_score = 0.0

    cnt = 0
    for f2p_m, p2f_m in mutant_feature_name_pairs:
        cnt += 1

        f2p = int(row[f2p_m])
        p2f = int(row[p2f_m])

        if f2p == -1:
            assert p2f == -1
            continue
        if p2f == -1:
            assert f2p == -1
            continue
    
        utilized_mutant_cnt += 1
        line_total_f2p += f2p
        line_total_p2f += p2f
    
    muse_1 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1)))
    muse_2 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1)))

    muse_3 = muse_1 * line_total_f2p
    muse_4 = muse_2 * line_total_p2f

    final_muse_score = muse_3 - muse_4

    return final_muse_score


def measure_susp_score(feature_file, totFailed_cnt, mutant_feature_name_pairs, total_f2p, total_p2f):
    susp_score_per_line = {}

    with open(feature_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            tot_failed_TCs_line = int(row['# of totfailed_TCs'])
            assert totFailed_cnt == tot_failed_TCs_line, f"Error: totFailed_cnt: {totFailed_cnt} != tot_failed_TCs_line: {tot_failed_TCs_line}"

            # STEP 3: MEASURE THE SUSPICIOUSNESS SCORE FOR EACH LINE
            metallaxis_score = measure_metallaxis(row, mutant_feature_name_pairs)
            muse_score = measure_muse(row, total_f2p, total_p2f, mutant_feature_name_pairs)

            line_key = row['key']
            assert line_key not in susp_score_per_line, f"Error: {key} already exists in susp_score_per_line"

            susp_score_per_line[line_key] = {
                'metallaxis': metallaxis_score,
                'muse': muse_score
            }
    
    return susp_score_per_line



def start_program(feature_file):
    target_filename = feature_file.name

    # STEP 1: BEGIN BY RETRIEVING THE META-DATA OF THE CURRENT BUG VERSION
    print("\nMeasuring Meta-Data of current Bug Version ...")
    totFailed_cnt, max_mutant_count = get_prerequite_data(feature_file)
    mutant_feature_name_pairs = get_mutant_feature_name_pairs(max_mutant_count)
    total_f2p, total_p2f = get_total_killed_count(feature_file, mutant_feature_name_pairs)

    print(f"Meta-Data of current Bug Version:")
    print(f"\tTotal Failed TCs: {totFailed_cnt}")
    print(f"\tTotal Mutants: {max_mutant_count}")
    print(f"\tTotal F2P: {total_f2p}")
    print(f"\tTotal P2F: {total_p2f}")


    # STEP 2: MEASURE THE SUSPICIOUSNESS SCORE
    print(f"\nMeasuring susp. score from {target_filename} ...")
    susp_score_per_line = measure_susp_score(feature_file, totFailed_cnt, mutant_feature_name_pairs, total_f2p, total_p2f)

    # STEP 4: WRITE THE SUSPICIOUSNESS SCORE TO A FILE
    print(f"\nWriting susp. score to file, susp_score.csv...")
    with open("susp_score.csv", 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['key', 'muse', 'metallaxis'])
        writer.writeheader()

        for key, value in susp_score_per_line.items():
            writer.writerow({
                'key': key,
                'muse': value['muse'],
                'metallaxis': value['metallaxis'],
            })



# /home/yangheechan/mbfl-dataset-gen/LIGNex1_FL_dataset/fl_datasets/fl_dataset-240419-v1/FL_features_per_bug_version/bug1.fl_features.csv
if __name__ == "__main__":
    parser = return_parser()
    args = parser.parse_args()
    
    feature_file = Path(args.feature_file)
    assert feature_file.exists(), f"Error: {feature_file} does not exist"
    
    start_program(feature_file)