import csv
import json
import shutil
from tqdm import tqdm
import random

from lib.utils import *
from lib.susp_score_formula import *
from analysis.rank_utils import *

from lib.experiment import Experiment
from lib.database import CRUD
from lib.susp_score_formula import *


class Postprocessor:
    def __init__(
        self, subject_name, experiment_name,
        mbfl_method, max_mutant_num, include_cct=False
    ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name
        self.mbfl_method = mbfl_method
        self.max_mutant_num = max_mutant_num
        self.include_cct = include_cct

        self.experiment = Experiment()
        # Settings for database
        self.host = self.experiment.experiment_config["database"]["host"]
        self.port = self.experiment.experiment_config["database"]["port"]
        self.user = self.experiment.experiment_config["database"]["user"]
        self.password = self.experiment.experiment_config["database"]["password"]
        self.database = self.experiment.experiment_config["database"]["database"]

        self.db = CRUD(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def run(self):
        # 0. Add missing features in line_info table
        self.add_missing_features()

        # 1. Calculate and write both sbfl and mbfl features
        self.calc_and_write_dynamic_features()
 
    

    def add_missing_features(self):
        # add sbfl features on line_info table
        for sbfl_features in pp_sbfl_formulas:
            feature_name = sbfl_features.lower()
            feature_name = feature_name.replace("+", "_")
            if not self.db.column_exists("line_info", feature_name):
                self.db.add_column("line_info", f"{feature_name} FLOAT DEFAULT NULL")
        
        # add muse_score, met_score on line_info table
        if not self.db.column_exists("line_info", "muse_score"):
            self.db.add_column("line_info", "muse_score FLOAT DEFAULT 0.0")
        if not self.db.column_exists("line_info", "met_score"):
            self.db.add_column("line_info", "met_score FLOAT DEFAULT 0.0")
    
    def calc_and_write_dynamic_features(self):
        # get target buggy version list
        target_buggy_version_list = self.get_target_buggy_version_list(self.subject_name, self.experiment_name, "mbfl")

        for buggy_version in tqdm(target_buggy_version_list, desc="Calculating dynamic features"):
            self.calc_and_write_mbfl_features(buggy_version)
            self.calc_and_write_sbfl_features(buggy_version)
    

    # ========================================
    # ========= SBFL related functions =======
    # ========================================
    def calc_and_write_sbfl_features(self, buggy_version):
        bug_idx = buggy_version[0]
        version = buggy_version[1]
        buggy_file = buggy_version[2]
        buggy_function = buggy_version[3]
        buggy_lineno = buggy_version[4]
        buggy_line_idx = buggy_version[5]
        num_failing_tcs = buggy_version[6]
        num_passing_tcs = buggy_version[7]
        num_ccts = buggy_version[8]

        # Get lines that we target to analyze for SBFL
        target_line_idx = self.db.read(
            "line_info",
            columns="line_idx, file, function, lineno",
            conditions={"bug_idx": bug_idx}
        )
        
    
        line2spectrum = self.get_spectrum(bug_idx)

        # Get SBFL scores for targetted lines
        line2sbfl = self.measure_sbfl_scores(line2spectrum, num_failing_tcs, num_passing_tcs, num_ccts)

        # Update line_info table with SBFL scores
        self.update_line_info_table_with_sbfl_scores(bug_idx, line2sbfl)
    
    def update_line_info_table_with_sbfl_scores(self, bug_idx, line2sbfl):
        """
        Update line_info table with SBFL scores
        """
        for line_idx, sbfl_scores in line2sbfl.items():

            self.db.update(
                "line_info",
                set_values=sbfl_scores,
                conditions={
                    "bug_idx": bug_idx,
                    "line_idx": line_idx
                }
            )

    
    def measure_sbfl_scores(self, line2spectrum, num_failing_tcs, num_passing_tcs, num_ccts):
        """
        Measure SBFL scores with given spectrum
        """
        line2sbfl = {}
        for line_idx, spectrum in line2spectrum.items():
            for sbfl_formula in pp_sbfl_formulas:
                ep, np, ef, nf = spectrum["ep"], spectrum["np"], spectrum["ef"], spectrum["nf"]
                total_fails = num_failing_tcs
                total_passes = num_passing_tcs
                if self.include_cct:
                    cct_ep, cct_np = spectrum["cct_ep"], spectrum["cct_np"]
                    ep += cct_ep
                    np += cct_np
                    total_passes += num_ccts
                

                sbfl_score = sbfl(
                    ep, ef, np, nf,
                    formula=sbfl_formula,
                    fails=total_fails, passes=total_passes
                )

                if line_idx not in line2sbfl:
                    line2sbfl[line_idx] = {}
                sbfl_formula_str = sbfl_formula.lower()
                sbfl_formula_str = sbfl_formula_str.replace("+", "_")
                assert sbfl_formula_str not in line2sbfl[line_idx], f"Error: {sbfl_formula_str} already exists in line2sbfl[{line_idx}]"
                line2sbfl[line_idx][sbfl_formula_str] = sbfl_score

        return line2sbfl

    def get_spectrum(self, bug_idx):
        """
        Get spectrum for bug_idx
        """
        columns = [
            "line_idx", "ep", "np", "ef", "nf", "cct_ep", "cct_np"
        ]
        col_str = ", ".join(columns)
        ret = self.db.read(
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

    # ========================================
    # ========= MBFL related functions =======
    # ========================================
    def calc_and_write_mbfl_features(self, buggy_version):
        bug_idx = buggy_version[0]
        version = buggy_version[1]
        buggy_file = buggy_version[2]
        buggy_function = buggy_version[3]
        buggy_lineno = buggy_version[4]
        buggy_line_idx = buggy_version[5]
        num_failing_tcs = buggy_version[6]

        # Get lines that we target to analyze for MBFL
        if self.mbfl_method == "for_random_mbfl":
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    self.mbfl_method: True
                },
                special=f"ORDER BY line_idx LIMIT {self.max_mutant_num}"
            )
        else:
            target_line_idx = self.db.read(
                "line_info",
                columns="line_idx, file, function, lineno",
                conditions={
                    "bug_idx": bug_idx,
                    self.mbfl_method: True
                },
                # special=f"ORDER BY {SBFL_STANDARD} LIMIT {num_lines_for_random}"
                # special=f"ORDER BY {SBFL_STANDARD}"
            )
        
        # map line_idx to line_info map
        line_idx2line_info = {}
        for row in target_line_idx:
            line_idx = row[0]
            line_info = {
                "file": row[1],
                "function": row[2],
                "lineno": row[3]
            }
            line_idx2line_info[line_idx] = line_info

        # Make sure to add buggy line to line_idx2line_info
        if buggy_line_idx not in line_idx2line_info:
            # remove randomly one line_idx in line_idx2line_info dict
            key_list = list(line_idx2line_info.keys())
            random.shuffle(key_list)
            line_idx2line_info.pop(key_list[0])

            line_idx2line_info[buggy_line_idx] = {
                "file": buggy_file,
                "function": buggy_function,
                "lineno": buggy_lineno
            }
        
        assert buggy_line_idx in line_idx2line_info, f"buggy_line_idx {buggy_line_idx} not in line_idx2line_info"

        # Get all mutants generated on target lines
        lines_idx2mutant_idx = self.get_mutations_on_target_lines(bug_idx, line_idx2line_info)
        
        # Measure MBFL score for targetted lines
        version_data = self.measure_mbfl_scores(
            line_idx2line_info, lines_idx2mutant_idx, num_failing_tcs, self.max_mutant_num
        )
        version_data["total_num_of_failing_tcs"] = num_failing_tcs

        # Update line_info table with met_score, muse_score
        self.update_line_info_table_with_mbfl_scores(bug_idx, line_idx2line_info, lines_idx2mutant_idx)


    def update_line_info_table_with_mbfl_scores(self, bug_idx, line_idx2line_info, lines_idx2mutant_idx):
        """
        Update line_info table with MBFL scores
        """
        for line_idx, line_info in line_idx2line_info.items():
            if line_idx not in lines_idx2mutant_idx:
                continue

            met_score = line_info["met_score"]
            muse_score = line_info["muse_score"]
            # print(f"BUG: {bug_idx}, Line {line_idx} - Metallaxis: {met_score}, MUSE: {muse_score}")
            
            self.db.update(
                "line_info",
                set_values={
                    "met_score": met_score,
                    "muse_score": muse_score
                },
                conditions={
                    "bug_idx": bug_idx,
                    "line_idx": line_idx
                }
            )

    
    def measure_mbfl_scores(self, line_idx2line_info, lines_idx2mutant_idx, total_num_of_failing_tcs, mtc):
        """
        Measure MBFL scores for a given number of mutants
        """
        # Select mtc mutants per line at random
        utilizing_line_idx2mutants, total_num_of_utilized_mutants = self.select_random_mtc_mutants_per_line(lines_idx2mutant_idx, mtc)

        # Calculate total information
        total_p2f, total_f2p = self.calculate_total_info(utilizing_line_idx2mutants)


        for line_idx, mutants in utilizing_line_idx2mutants.items():
            # print(f"Analyzing line {line_idx}")

            met_data = self.measure_metallaxis(mutants, total_num_of_failing_tcs)
            muse_data = self.measure_muse(mutants, total_p2f, total_f2p)

            # met_score, muse_score = met_data["met_score"], muse_data["muse_score"]
            # print(f"\tMetallaxis score: {met_score}")
            # print(f"\tMUSE score: {muse_score}")

            line_idx2line_info[line_idx]["met_score"] = met_data["met_score"]
            line_idx2line_info[line_idx]["muse_score"] = muse_data["muse_score"]
        
        mtc_version_data = {"total_num_of_utilized_mutants": total_num_of_utilized_mutants}

        return  mtc_version_data
    
    def measure_metallaxis(self, mutants, total_num_of_failing_tcs):
        """
        Measure Metallaxis score
        """
        met_score_list = []

        for mutant in mutants:
            f2p = mutant["f2p"]
            p2f = mutant["p2f"]
            if self.include_cct:
                p2f += mutant["p2f_cct"]
            
            score = 0.0
            if f2p + p2f == 0.0:
                score = 0.0
            else:
                score = ((f2p) / math.sqrt(total_num_of_failing_tcs * (f2p + p2f)))
            
            met_score_list.append(score)
        
        if len(met_score_list) == 0:
            return {
                "total_num_of_failing_tcs": total_num_of_failing_tcs,
                "met_score": 0.0
            }

        final_met_score = max(met_score_list)
        met_data = {
            "total_num_of_failing_tcs": total_num_of_failing_tcs,
            "met_score": final_met_score
        }
        return met_data
    

    def measure_muse(self, mutants, total_p2f, total_f2p):
        utilized_mutant_cnt = len(mutants)
        line_total_p2f = 0
        line_total_f2p = 0

        final_muse_score = 0.0

        for mutant in mutants:
            line_total_p2f += mutant["p2f"]
            line_total_f2p += mutant["f2p"]
            if self.include_cct:
                line_total_p2f += mutant["p2f_cct"]
        
        muse_1 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1)))
        muse_2 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1)))

        muse_3 = muse_1 * line_total_f2p
        muse_4 = muse_2 * line_total_p2f

        final_muse_score = muse_3 - muse_4

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
            "muse_score": final_muse_score
        }

        return muse_data

    def calculate_total_info(self, utilizing_line_idx2mutants):
        """
        Calculate total information for selected mutants
            - total_p2f, total_f2p, total_build_time, total_tc_execution_time
        """

        total_p2f = 0
        total_f2p = 0

        for line_idx, mutants in utilizing_line_idx2mutants.items():
            for mutant in mutants:
                total_p2f += mutant["p2f"]
                total_f2p += mutant["f2p"]
                if self.include_cct:
                    total_p2f += mutant["p2f_cct"]

        return total_p2f, total_f2p

    def select_random_mtc_mutants_per_line(self, lines_idx2mutant_idx, mtc):
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
    
    def get_mutations_on_target_lines(self, bug_idx, line_idx2line_info):
        """
        Get mutations on target lines
        """
        columns = [
            "line_idx", "mutant_idx", "build_result",
            "f2p", "p2f", "f2f", "p2p", "p2f_cct", "p2p_cct"
        ]
        col_str = ", ".join(columns)
        special_str = f"AND line_idx IN ({', '.join([str(line_idx) for line_idx in line_idx2line_info])})"
        ret = self.db.read(
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
                }
            )
        
        return lines_idx2mutant_idx


    def get_target_buggy_version_list(self, subject_name, experiment_name, stage):
        """
        Get list of buggy versions that meet the criteria
        """
        columns = [
            "bug_idx", "version", "buggy_file", "buggy_function", "buggy_lineno", "buggy_line_idx",
            "num_failing_tcs", "num_passing_tcs", "num_ccts"
        ]
        col_str = ", ".join(columns)
        return self.db.read(
            "bug_info",
            columns=col_str,
            conditions={
                "subject": subject_name,
                "experiment_name": experiment_name,
                stage: True
            }
        )
    
