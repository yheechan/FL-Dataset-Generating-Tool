import random
import math

from lib.susp_score_formula import *

def get_target_buggy_version_list(subject_name, experiment_name, stage, db):
    """
    Get list of buggy versions that meet the criteria
    """
    columns = [
        "bug_idx", "version", "buggy_file", "buggy_function", "buggy_lineno", "buggy_line_idx",
        "num_failing_tcs", "num_passing_tcs", "num_ccts", "num_total_lines"
    ]
    col_str = ", ".join(columns)
    return db.read(
        "bug_info",
        columns=col_str,
        conditions={
            "subject": subject_name,
            "experiment_name": experiment_name,
            stage: True
        }
    )

# ========================================
# ========= MBFL related functions =======
# ========================================
def get_mutations_on_target_lines(bug_idx, line_idx2line_info, db):
    """
    Get mutations on target lines
    """
    columns = [
        "line_idx", "mutant_idx", "build_result",
        "f2p", "p2f", "f2f", "p2p", "p2f_cct", "p2p_cct",
        "build_time_duration", "tc_execution_time_duration", "ccts_execution_time_duration"
    ]
    col_str = ", ".join(columns)
    special_str = f"AND line_idx IN ({', '.join([str(line_idx) for line_idx in line_idx2line_info])})"
    ret = db.read(
        "mutation_info",
        columns=col_str,
        conditions={
            "bug_idx": bug_idx,
            "is_for_test": True
        },
        special=special_str
    )


    # Map line_idx to mutant_idx
    lines_idx2mutant_idx = {}
    for row in ret:
        line_idx = row[0]
        if line_idx not in lines_idx2mutant_idx:
            lines_idx2mutant_idx[line_idx] = []
        lines_idx2mutant_idx[line_idx].append(
            {
                "mutant_idx": row[1],
                "build_result": row[2],
                "f2p": row[3],
                "p2f": row[4],
                "f2f": row[5],
                "p2p": row[6],
                "p2f_cct": row[7],
                "p2p_cct": row[8],
                "build_time_duration": row[9],
                "tc_execution_time_duration": row[10],
                "ccts_execution_time_duration": row[11]
            }
        )
    
    return lines_idx2mutant_idx

def measure_mbfl_scores(line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc, analysis_config):
    """
    Measure MBFL scores for a given number of mutants
    """
    # Select mtc mutants per line at random
    utilizing_line_idx2mutants, total_num_of_utilized_mutants = select_random_mtc_mutants_per_line(lines_idx2mutant_idx, mtc)
    # print(f"Total number of utilized mutants: {total_num_of_utilized_mutants}")
    # print(f"utilizing_line_idx2mutants: {len(utilizing_line_idx2mutants)}")

    # Calculate total information
    total_p2f, total_f2p, \
        total_build_time, total_tc_execution_time \
        = calculate_total_info(utilizing_line_idx2mutants, analysis_config["include_cct"])


    for line_idx, mutants in utilizing_line_idx2mutants.items():
        # print(f"Analyzing line {line_idx}")

        met_data = measure_metallaxis(mutants, total_num_of_failing_tcs, analysis_config["include_cct"])
        muse_data = measure_muse(mutants, total_p2f, total_f2p, analysis_config["include_cct"])

        # met_score, muse_score = met_data["met_score"], muse_data["muse_score"]
        # print(f"\tMetallaxis score: {met_score}")
        # print(f"\tMUSE score: {muse_score}")

        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            for sub_form in sub_form_list:
                if "met" in mbfl_form:
                    line_idx2line_info[line_idx][sub_form] = met_data[sub_form]
                elif "muse" in mbfl_form:
                    line_idx2line_info[line_idx][sub_form] = muse_data[sub_form]
    
    mtc_version_data = {
        "total_num_of_utilized_mutants": total_num_of_utilized_mutants,
        "total_build_time": total_build_time,
        "total_tc_execution_time": total_tc_execution_time
    }

    return  mtc_version_data

def select_random_mtc_mutants_per_line(lines_idx2mutant_idx, mtc):
    """
    Select mtc mutants per line at random
    """
    selected_mutants = {}
    total_num_of_utilized_mutants = 0
    for line_idx in lines_idx2mutant_idx:
        mutants = lines_idx2mutant_idx[line_idx]
        random.shuffle(mutants)
        selected_mutants[line_idx] = []
        for mutant in mutants:
            if len(selected_mutants[line_idx]) == mtc:
                break
            if mutant["build_result"] == False:
                continue
            selected_mutants[line_idx].append(mutant)
            total_num_of_utilized_mutants += 1
    return selected_mutants, total_num_of_utilized_mutants


def calculate_total_info(utilizing_line_idx2mutants, include_cct=False):
    """
    Calculate total information for selected mutants
        - total_p2f, total_f2p, total_build_time, total_tc_execution_time
    """

    total_p2f = 0
    total_f2p = 0
    total_build_time = 0
    total_tc_execution_time = 0

    for line_idx, mutants in utilizing_line_idx2mutants.items():
        for mutant in mutants:
            total_p2f += mutant["p2f"]
            total_f2p += mutant["f2p"]
            total_build_time += mutant["build_time_duration"]
            total_tc_execution_time += mutant["tc_execution_time_duration"]
            if include_cct:
                total_p2f += mutant["p2f_cct"]
                total_tc_execution_time += mutant["ccts_execution_time_duration"]

    return total_p2f, total_f2p, total_build_time, total_tc_execution_time

def measure_metallaxis(mutants, total_num_of_failing_tcs, include_cct=False):
    """
    Measure Metallaxis score
    """

    met_2_score_list = []
    met_3_score_list = []
    f2p_list = []
    for mutant in mutants:
        f2p = mutant["f2p"]
        f2p_list.append(f2p)
        p2f = mutant["p2f"]
        if include_cct:
            p2f += mutant["p2f_cct"]
        
        met_2_score = 0.0
        met_3_score = 0.0
        if f2p + p2f == 0.0:
            met_2_score = 0.0
            met_3_score = 0.0
        else:
            met_2_score = (1 / math.sqrt(f2p + p2f))
            met_3_score = ((f2p) / math.sqrt(total_num_of_failing_tcs * (f2p + p2f)))
        
        met_2_score_list.append(met_2_score)
        met_3_score_list.append(met_3_score)
    
    if len(met_3_score_list) == 0:
        return {
            "total_num_of_failing_tcs": total_num_of_failing_tcs,
            "met_1": -10.0,
            "met_2": -10.0,
            "met_3": -10.0
        }

    met_1 = max(f2p_list)
    met_2 = max(met_2_score_list)
    met_3 = max(met_3_score_list)
    met_data = {
        "total_num_of_failing_tcs": total_num_of_failing_tcs,
        "met_1": met_1,
        "met_2": met_2,
        "met_3": met_3,
    }
    return met_data


def measure_muse(mutants, total_p2f, total_f2p, include_cct=False):
    """
    Measure MUSE score
    """
    utilized_mutant_cnt = len(mutants)
    line_total_p2f = 0
    line_total_f2p = 0

    final_muse_score = 0.0

    for mutant in mutants:
        line_total_p2f += mutant["p2f"]
        line_total_f2p += mutant["f2p"]
        if include_cct:
            line_total_p2f += mutant["p2f_cct"]
    
    muse_1 = 1 / (utilized_mutant_cnt + 1)

    muse_2 = line_total_f2p
    muse_3 = line_total_p2f

    muse_4 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1))) * line_total_f2p
    muse_5 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1))) * line_total_p2f

    muse_6 = muse_4 - muse_5

    muse_data = {
        "utilized_mutant_cnt": utilized_mutant_cnt,
        "total_f2p": total_f2p,
        "total_p2f": total_p2f,
        "line_total_f2p": line_total_f2p,
        "line_total_p2f": line_total_p2f,
        "muse_1": muse_1,
        "muse_2": muse_2,
        "muse_3": muse_3,
        "muse_4": muse_4,
        "muse_5": muse_5,
        "muse_6": muse_6,
    }

    return muse_data


def update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx, db):
    """
    Update line_info table with MBFL scores
    """
    for line_idx, line_info in line_idx2line_info.items():
        if line_idx not in lines_idx2mutant_idx:
            continue

        values = {}
        for mbfl_form, sub_form_list in final_mbfl_formulas.items():
            for sub_form in sub_form_list:
                values[sub_form] = line_info[sub_form]
        
        db.update(
            "line_info",
            set_values=values,
            conditions={
                "bug_idx": bug_idx,
                "line_idx": line_idx
            }
        )


# ========================================
# ========= SBFL related functions =======
# ========================================
def update_line_info_table_with_sbfl_scores(bug_idx, line2sbfl, db):
    """
    Update line_info table with SBFL scores
    """
    for line_idx, sbfl_scores in line2sbfl.items():

        db.update(
            "line_info",
            set_values=sbfl_scores,
            conditions={
                "bug_idx": bug_idx,
                "line_idx": line_idx
            }
        )

    
def measure_sbfl_scores(line2spectrum, num_failing_tcs, num_passing_tcs, num_ccts, include_cct):
    """
    Measure SBFL scores with given spectrum
    """
    line2sbfl = {}
    for line_idx, spectrum in line2spectrum.items():
        for sbfl_formula, sub_form_list in final_sbfl_formulas.items():
            ep, np, ef, nf = spectrum["ep"], spectrum["np"], spectrum["ef"], spectrum["nf"]
            total_fails = num_failing_tcs
            total_passes = num_passing_tcs
            if include_cct:
                cct_ep, cct_np = spectrum["cct_ep"], spectrum["cct_np"]
                ep += cct_ep
                np += cct_np
                total_passes += num_ccts
            
            for sub_form in sub_form_list:
                sbfl_score = sbfl(
                    ep, ef, np, nf,
                    formula=sub_form,
                    fails=total_fails, passes=total_passes
                )

                if line_idx not in line2sbfl:
                    line2sbfl[line_idx] = {}
                sub_form_str = sub_form.lower()
                sub_form_str = sub_form_str.replace("+", "_")
                assert sub_form_str not in line2sbfl[line_idx], f"Error: {sub_form_str} already exists in line2sbfl[{line_idx}]"
                line2sbfl[line_idx][sub_form_str] = sbfl_score

    return line2sbfl

def get_spectrum(bug_idx, db):
    """
    Get spectrum for bug_idx
    """
    columns = [
        "line_idx", "ep", "np", "ef", "nf", "cct_ep", "cct_np"
    ]
    col_str = ", ".join(columns)
    ret = db.read(
        "line_info",
        columns=col_str,
        conditions={"bug_idx": bug_idx}
    )

    line2spectrum = {}

    for row in ret:
        line_idx = row[0]
        line2spectrum[line_idx] = {
            "ep": row[1],
            "np": row[2],
            "ef": row[3],
            "nf": row[4],
            "cct_ep": row[5],
            "cct_np": row[6]
        }
    
    return line2spectrum