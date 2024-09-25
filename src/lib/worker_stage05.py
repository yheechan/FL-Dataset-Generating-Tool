import subprocess as sp
import random
import csv

from lib.utils import *
from lib.worker_base import Worker
from lib.susp_score_formula import *

class WorkerStage05(Worker):
    def __init__(
            self, subject_name, machine, core, version_name, verbose=False):
        super().__init__(subject_name, "stage05", "extracting_sbfl_features", machine, core, verbose)
        
        self.assigned_works_dir = self.core_dir / f"stage05-assigned_works"
        self.version_name = version_name

        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.target_code_file, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_dir)
        self.target_code_file_path = self.core_dir / self.target_code_file
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.version_dir)
        self.set_lines_executed_by_failing_tc(self.version_dir, self.target_code_file, self.buggy_lineno)
        self.set_line2function_dict(self.version_dir)

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)
        
        self.buggy_line_key = self.make_key(self.target_code_file, self.buggy_lineno)
        buggy_line_key_from_data = get_buggy_line_key_from_data(self.version_dir)
        assert self.buggy_line_key == buggy_line_key_from_data, f"Buggy line key {self.buggy_line_key} does not match with buggy line key from data {buggy_line_key_from_data}"

        self.core_repo_dir = self.core_dir / self.name

        self.sbfl_features_dir = out_dir / f"{self.name}" / "sbfl_features"
        self.sbfl_features_dir.mkdir(exist_ok=True, parents=True)

        self.postprocessed_cov_file = self.version_dir / "coverage_info" / "postprocessed_coverage.csv"
        assert self.postprocessed_cov_file.exists(), f"Postprocessed coverage file {self.postprocessed_cov_file} does not exist"

        self.postprocessed_cov_noCCTs_file = self.version_dir / "coverage_info" / "postprocessed_coverage_noCCTs.csv"
        assert self.postprocessed_cov_noCCTs_file.exists(), f"Postprocessed coverage file without CCTs {self.postprocessed_cov_noCCTs_file} does not exist"

        self.lines_from_pp_cov = self.get_lines_from_pp_cov_as_dict(self.postprocessed_cov_file)
        self.lines_from_pp_cov_noCCTs = self.get_lines_from_pp_cov_as_dict(self.postprocessed_cov_noCCTs_file, noCCTs=True)

    def run(self):
        # 1. initialize spectrum per line
        self.spectrum_per_line = self.init_spectrum_per_line(self.lines_from_pp_cov)

        # 2. calculate suspiciousness score
        sbfl_per_line = self.measure_total_sbfl(self.spectrum_per_line)

        # 3. write suspiciousness scores to file
        self.write_sbfl_features(self.version_dir, sbfl_per_line)




        # 1. initialize spectrum per line without CCTs
        self.spectrum_per_line_noCCTs = self.init_spectrum_per_line(self.lines_from_pp_cov_noCCTs)

        # 2. calculate suspiciousness score without CCTs
        sbfl_per_line_noCCTs = self.measure_total_sbfl(self.spectrum_per_line_noCCTs)

        # 3. write suspiciousness scores without CCTs to file
        self.write_sbfl_features(self.version_dir, sbfl_per_line_noCCTs, noCCTs=True)



        # 4. save the version directory to self.sbfl_features_dir
        self.save_version(self.version_dir, self.sbfl_features_dir)
    
    def init_spectrum_per_line(self, lines_from_pp_cov):
        spectrums_per_line = []
        buggy_line_cnt = 0
        for line in self.lines_from_pp_cov:
            line_key = line['key']

            bug_stat = 0
            if line_key == self.buggy_line_key:
                assert buggy_line_cnt == 0, f"Multiple buggy lines found: {self.buggy_line_key}"
                buggy_line_cnt += 1
                bug_stat = 1
            
            ef, nf = calculate_spectrum(line, self.failing_tcs_list)
            ep, np = calculate_spectrum(line, self.passing_tcs_list)

            # VALIDATE: sum of executed and not executed test cases should be equal to total number of test cases
            assert ef + nf == len(self.failing_tcs_list), f"Sum of executed test cases {ef} and not executed test cases {ep} should be equal to total number of failing test cases {len(self.failing_tcs_list)}"
            assert ep + np == len(self.passing_tcs_list), f"Sum of executed test cases {nf} and not executed test cases {np} should be equal to total number of passing test cases {len(self.passing_tcs_list)}"

            spectrums_per_line.append({
                'key': line_key,
                'ep': ep, 'ef': ef, 'np': np, 'nf': nf,
                'bug': bug_stat
            })

        return spectrums_per_line
    
    def measure_total_sbfl(self, spectrums_per_line):
        for line_info in spectrums_per_line:
            ep = line_info["ep"]
            ef = line_info["ef"]
            np = line_info["np"]
            nf = line_info["nf"]

            for sbfl_formula in sbfl_formulas:
                sbfl_value = sbfl(ep, ef, np, nf, sbfl_formula)
                line_info[sbfl_formula] = sbfl_value
        return spectrums_per_line
    
    def write_sbfl_features(self, version_dir, spectrum_per_line, noCCTs=False):
        filename = "sbfl_features.csv"
        if noCCTs:
            filename = "sbfl_features_noCCTs.csv"

        sbfl_features_csv = version_dir / filename

        with open(sbfl_features_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'key', 'ep', 'ef', 'np', 'nf',
                'Binary', 'GP13', 'Jaccard', 'Naish1',
                'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1',
                'bug'
            ])
            writer.writeheader()

            for line_info in spectrum_per_line:
                writer.writerow(line_info)
