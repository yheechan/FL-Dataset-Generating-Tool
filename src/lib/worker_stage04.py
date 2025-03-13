import subprocess as sp
import random
import csv

from lib.utils import *
from lib.worker_base import Worker
from lib.susp_score_formula import *

class WorkerStage04(Worker):
    def __init__(
            self, subject_name, experiment_name, machine, core, version_name, verbose=False):
        super().__init__(subject_name, "stage04", "extracting_sbfl_features", machine, core, verbose)

        self.experiment_name = experiment_name
        
        self.assigned_works_dir = self.core_dir / f"stage04-assigned_works"
        self.version_name = version_name

        self.version_name = version_name
        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.connect_to_db()
        self.bug_idx = self.get_bug_idx(self.name, self.experiment_name, version_name)
        self.target_code_file, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.bug_idx)
        self.target_code_file_path = self.core_dir / self.target_code_file
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.bug_idx)
        self.set_lines_executed_by_failing_tc(self.version_dir, self.target_code_file, self.buggy_lineno)
        self.set_line2function_dict(self.version_dir)

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)
        
        self.buggy_line_key = self.get_buggy_line_key(self.bug_idx)

        self.core_repo_dir = self.core_dir / self.name

        self.line_data = self.get_lines_from_line_info_table()
        self.cov_per_tc_data = self.get_cov_per_tc_data()
    
    def get_lines_from_line_info_table(self):
        res = self.db.read(
            "line_info",
            columns="line_idx, file, function, lineno",
            conditions={"bug_idx": self.bug_idx},
            special="ORDER BY line_idx ASC"
        )
        line_data = []
        for num, row in enumerate(res):
            line_idx = row[0]
            assert num == line_idx, f"Line index {line_idx} does not match with expected line index {num}"

            file = row[1]
            function = row[2]
            linno = row[3]

            line_data.append({
                "file": file,
                "function": function,
                "lineno": linno,
                "sbfl_data": {
                    "ep": 0, "ef": 0, "np": 0, "nf": 0,
                    "cct_ep": 0, "cct_np": 0,
                }
            })
        return line_data

    def get_cov_per_tc_data(self):
        res = self.db.read(
            "tc_info",
            columns="tc_name, tc_result, cov_bit_seq",
            conditions={"bug_idx": self.bug_idx}
        )
        cov_per_tc_data = {"pass": [], "fail": [], "cct": []}
        for row in res:
            tc_name = row[0]
            tc_result = row[1]
            cov_bit_seq = row[2]

            if tc_result == "pass":
                cov_per_tc_data["pass"].append((tc_name, cov_bit_seq))
            elif tc_result == "fail":
                cov_per_tc_data["fail"].append((tc_name, cov_bit_seq))
            elif tc_result == "cct":
                cov_per_tc_data["cct"].append((tc_name, cov_bit_seq))
        return cov_per_tc_data


            
    def run(self):
        # 1. initialize spectrum per line: Updates self.line_data with ep, np, nf, ef, cct_ep, cct_np
        self.init_spectrum_per_line()

        # 2. calculate suspiciousness score
        self.measure_total_sbfl()

        # 3. write suspiciousness scores to file
        self.write_sbfl_features()

        # 4. save the version directory to self.sbfl_features_dir
        self.save_version(self.bug_idx, "sbfl")
    
    def init_spectrum_per_line(self):
        for key, cov_per_tc in self.cov_per_tc_data.items():
            for cov_info in cov_per_tc:
                tc_script_name = cov_info[0]
                cov_bit_seq = cov_info[1]

                for line_idx, line_cov in enumerate(cov_bit_seq):
                    if key == "pass" and line_cov =="1":
                        self.line_data[line_idx]["sbfl_data"]["ep"] += 1
                    elif key == "pass" and line_cov == "0":
                        self.line_data[line_idx]["sbfl_data"]["np"] += 1
                    elif key == "fail" and line_cov == "1":
                        self.line_data[line_idx]["sbfl_data"]["ef"] += 1
                    elif key == "fail" and line_cov == "0":
                        self.line_data[line_idx]["sbfl_data"]["nf"] += 1
                    elif key == "cct" and line_cov == "1":
                        self.line_data[line_idx]["sbfl_data"]["cct_ep"] += 1
                    elif key == "cct" and line_cov == "0":
                        self.line_data[line_idx]["sbfl_data"]["cct_np"] += 1

    
    def measure_total_sbfl(self):
        # sbfl_list = sbfl_formulas
        sbfl_list = []
        for form, sub_form_list in final_sbfl_formulas.items():
            sbfl_list.extend(sub_form_list)

        for line_info in self.line_data:
            file = line_info["file"]
            func = line_info["function"]
            lineno = line_info["lineno"]

            ep = line_info["sbfl_data"]["ep"]
            ef = line_info["sbfl_data"]["ef"]
            np = line_info["sbfl_data"]["np"]
            nf = line_info["sbfl_data"]["nf"]
            cct_ep = line_info["sbfl_data"]["cct_ep"]
            cct_np = line_info["sbfl_data"]["cct_np"]

            for sbfl_formula in sbfl_list:
                sbfl_value = sbfl(ep, ef, np, nf, sbfl_formula)
                line_info["sbfl_data"][sbfl_formula] = sbfl_value
            
            # for sbfl_formula in sbfl_list:
            #     sbfl_value = sbfl(ep+cct_ep, np+cct_np, np, nf, sbfl_formula)
            #     form_name = f"{sbfl_formula}_cct"
            #     line_info["sbfl_data"][form_name] = sbfl_value
        
    
    def write_sbfl_features(self, batch_size=250):
        """
        Optimized update for line_info using CASE and batched queries, 
        where line_idx is sequential and corresponds to the list index in line_data.
        """
        for i in range(0, len(self.line_data), batch_size):
            batch = self.line_data[i:i + batch_size]

            # Build SET clauses for each column in sbfl_data
            set_clauses = []
            for key in batch[0]["sbfl_data"].keys():  # Iterate over sbfl_data keys
                case_clause = " ".join(
                    [f"WHEN {idx} THEN %s" for idx, _ in enumerate(batch, start=i)]
                )
                set_clauses.append(f"{key} = CASE line_idx {case_clause} END")

            set_clause_str = ", ".join(set_clauses)

            # Prepare WHERE clause
            where_clause = f"line_idx BETWEEN {i} AND {i + len(batch) - 1}"

            # Construct query
            query = f"""
            UPDATE line_info
            SET {set_clause_str}
            WHERE bug_idx = %s AND {where_clause};
            """

            # Prepare values for placeholders
            values = []
            for key in batch[0]["sbfl_data"].keys():
                values.extend(line["sbfl_data"][key] for line in batch)

            values.append(self.bug_idx)  # Add bug_idx for WHERE clause

            # Execute the query
            self.db.cursor.execute(query, values)

        # Commit after all batches are processed
        self.db.commit()
