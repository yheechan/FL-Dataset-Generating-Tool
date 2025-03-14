import csv

from lib.utils import *
from analysis.rank_utils import *
from lib.susp_score_formula import *
from analysis.individual import Individual

from lib.experiment import Experiment
from lib.database import CRUD

class Validate:
    def __init__(
            self, subject_name, experiment_name
        ):
        self.subject_name = subject_name
        self.experiment_name = experiment_name

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
    

    def run(self, validation_criteria):
        if 0 in validation_criteria:
            self.val01()
            self.val02()
            self.val03()
            self.val04()
            self.val05()
            self.val06()
            self.val07()
            self.val08()
            self.val09()
            self.val10()
            self.val11()
            self.val12()
        else:
            for val_type in validation_criteria:
                if val_type == 1:
                    self.val01()
                elif val_type == 2:
                    self.val02()
                elif val_type == 3:
                    self.val03()
                elif val_type == 4:
                    self.val04()
                elif val_type == 5:
                    self.val05()
                elif val_type == 6:
                    self.val06()
                elif val_type == 7:
                    self.val07()
                elif val_type == 8:
                    self.val08()
                elif val_type == 9:
                    self.val09()
                elif val_type == 10:
                    self.val10()
                elif val_type == 11:
                    self.val11()
                elif val_type == 12:
                    self.val12()
    
    def val01(self):
        """
        [stage03] val01: Validate that all usable buggy versions
            consists 1 buggy line in line_info table
        """
        columns = [
            "b.buggy_file", "b.buggy_function", "b.buggy_lineno", "b.buggy_line_idx",
            "l.file", "l.function", "l.lineno", "l.line_idx", "l.is_buggy_line"
        ]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON l.bug_idx = b.bug_idx
            WHERE l.is_buggy_line IS TRUE
                AND b.subject = '{self.subject_name}'
                AND b.experiment_name = '{self.experiment_name}'
                AND b.prerequisites is TRUE
        """

        res = self.db.read(
            "line_info l",
            columns=col_str,
            special=special_str
        )

        for row in res:
            buggy_file = row[0]
            buggy_function = row[1]
            buggy_lineno = row[2]
            buggy_line_idx = row[3]

            line_file = row[4]
            line_function = row[5]
            line_lineno = row[6]
            line_line_idx = row[7]

            is_buggy_line = row[8]

            assert is_buggy_line == True, f"Line {line_lineno} in {line_file} is not a buggy line"

            assert buggy_file == line_file, f"Buggy file {buggy_file} does not match with line file {line_file}"
            assert buggy_function == line_function, f"Buggy function {buggy_function} does not match with line function {line_function}"
            assert buggy_lineno == line_lineno, f"Buggy line number {buggy_lineno} does not match with line line number {line_lineno}"
            assert buggy_line_idx == line_line_idx, f"Buggy line index {buggy_line_idx} does not match with line line index {line_line_idx}"

        print(f"[stage03-VAL01] {len(res)} buggy version with prerequisites=TRUE have valid line information with single buggy line")
    
    def val02(self):
        """
        [stage03] val02: Validate that all cov_bit_seq sequences in tc_info have the same length 
            as the number of lines in line_info for each bug_idx where 
            prerequisites is TRUE in bug_info.
        """
        columns = [
            "b.bug_idx", "COUNT(l.line_idx) AS line_count"
        ]
        col_str = ", ".join(columns)

        # Join bug_info with line_info to get the line count for each bug_idx
        special_str = f"""
            INNER JOIN line_info l ON b.bug_idx = l.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
            GROUP BY b.bug_idx
        """

        # Fetch the line count for each bug_idx
        line_info_res = self.db.read(
            "bug_info b",
            columns=col_str,
            special=special_str
        )

        # Prepare a dictionary to store line counts by bug_idx
        line_counts = {row[0]: row[1] for row in line_info_res}

        # Fetch cov_bit_seq and bug_idx from tc_info
        columns = ["t.bug_idx", "t.cov_bit_seq"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON t.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
            AND t.tc_result != 'crash'
        """

        tc_info_res = self.db.read(
            "tc_info t",
            columns=col_str,
            special=special_str
        )

        # Validate the length of cov_bit_seq against line counts
        for row in tc_info_res:
            bug_idx = row[0]
            cov_bit_seq = row[1]

            # Ensure bug_idx exists in line counts
            assert bug_idx in line_counts, f"bug_idx {bug_idx} not found in line_info results"

            # Ensure the bit length matches the line count
            expected_length = line_counts[bug_idx]
            actual_length = len(cov_bit_seq)
            assert actual_length == expected_length, (
                f"cov_bit_seq length {actual_length} does not match line count {expected_length} "
                f"for bug_idx {bug_idx}"
            )
        
        print(f"[stage03-VAL02] {len(tc_info_res)} test cases from {len(line_counts)} buggy versions with prerequisite=TRUE have valid cov_bit_seq sequences")

    def val03(self):
        """
        [stage03] val03: Validate that all test cases and coverage statistics for all buggy versions
            resulting from prerequisite data preparation has been recorded on bug_info table
        """
        columns = [
            "num_failing_tcs", "num_passing_tcs", "num_ccts", "num_total_tcs",
            "num_lines_executed_by_failing_tcs", "num_lines_executed_by_passing_tcs",
            "num_lines_executed_by_ccts", "num_total_lines_executed",
            "num_total_lines"
        ]
        col_str = ", ".join(columns)

        res = self.db.read(
            "bug_info",
            columns=col_str,
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name,
                "prerequisites": True
            }
        )

        for row in res:
            for col in row:
                assert col is not None, f"Column {col} is None"
        
        print(f"[stage03-VAL03] {len(res)} buggy versions with prerequisites=TRUE have valid test cases and coverage statistics")

    def val04(self):
        """
        [stage03] val04: Validate that all failing test cases from all buggy versions
            resulting from prerequisite data preparation executes the buggy line
        """
        # Step 1: Fetch all line_idx values where is_buggy_line IS TRUE for each bug_idx
        columns = ["b.bug_idx", "l.line_idx"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN line_info l ON b.bug_idx = l.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
            AND l.is_buggy_line IS TRUE
        """

        buggy_lines_res = self.db.read(
            "bug_info b",
            columns=col_str,
            special=special_str
        )

        # Step 2: Group line_idx values by bug_idx
        buggy_lines_map = {}
        for row in buggy_lines_res:
            bug_idx = row[0]
            line_idx = row[1]
            assert bug_idx is not None, f"bug_idx is None"
            if bug_idx not in buggy_lines_map:
                buggy_lines_map[bug_idx] = []
            buggy_lines_map[bug_idx].append(line_idx)

        # Step 3: Fetch cov_bit_seq for all test cases in tc_info for each bug_idx
        columns = ["t.bug_idx", "t.cov_bit_seq"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON t.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
            AND t.tc_result = 'fail'
        """

        tc_info_res = self.db.read(
            "tc_info t",
            columns=col_str,
            special=special_str
        )

        # Step 4: Validate that the nth bit in cov_bit_seq is "1" for all buggy line_idx
        for row in tc_info_res:
            bug_idx = row[0]
            cov_bit_seq = row[1]

            # Get buggy line indexes for this bug_idx
            buggy_lines = buggy_lines_map.get(bug_idx, [])

            for line_idx in buggy_lines:
                # Ensure the nth bit in cov_bit_seq is "1"
                if line_idx >= len(cov_bit_seq):
                    raise AssertionError(
                        f"Line index {line_idx} exceeds bit sequence length in cov_bit_seq for bug_idx {bug_idx}"
                    )
                assert cov_bit_seq[line_idx] == "1", (
                    f"cov_bit_seq does not have '1' at index {line_idx} for bug_idx {bug_idx}"
                )

        print(f"[stage03-VAL04] {len(tc_info_res)} failing test cases from {len(buggy_lines_map)} buggy versions with prerequisites=TRUE execute buggy line")

    def val05(self):
        """
        [stage03] val04: Validate that for each bug_idx in bug_info with prerequisites IS TRUE:
            1. num_failing_tcs > 0 and num_passing_tcs > 0.
            2. The number of rows in tc_info with tc_result='fail' matches num_failing_tcs.
            3. The number of rows in tc_info with tc_result='pass' matches num_passing_tcs.
        """

        # Step 1: Fetch num_failing_tcs and num_passing_tcs for each bug_idx
        columns = ["b.bug_idx", "b.num_failing_tcs", "b.num_passing_tcs"]
        col_str = ", ".join(columns)

        special_str = f"""
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
        """

        bug_info_res = self.db.read(
            "bug_info b",
            columns=col_str,
            special=special_str
        )

        # Step 2: Fetch counts of tc_result='fail' and tc_result='pass' for each bug_idx from tc_info
        columns = ["t.bug_idx", 
                "SUM(CASE WHEN t.tc_result = 'fail' THEN 1 ELSE 0 END) AS fail_count", 
                "SUM(CASE WHEN t.tc_result = 'pass' THEN 1 ELSE 0 END) AS pass_count"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON t.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
            GROUP BY t.bug_idx
        """

        tc_info_res = self.db.read(
            "tc_info t",
            columns=col_str,
            special=special_str
        )

        # Step 3: Map tc_info counts by bug_idx
        tc_counts_map = {row[0]: {"fail_count": row[1], "pass_count": row[2]} for row in tc_info_res}

        # Step 4: Validate conditions for each bug_idx
        for row in bug_info_res:
            bug_idx = row[0]
            num_failing_tcs = row[1]
            num_passing_tcs = row[2]

            # Ensure num_failing_tcs and num_passing_tcs are greater than 0
            assert num_failing_tcs > 0, f"num_failing_tcs is not greater than 0 for bug_idx {bug_idx}"
            assert num_passing_tcs > 0, f"num_passing_tcs is not greater than 0 for bug_idx {bug_idx}"

            # Validate the counts from tc_info
            if bug_idx in tc_counts_map:
                fail_count = tc_counts_map[bug_idx]["fail_count"]
                pass_count = tc_counts_map[bug_idx]["pass_count"]

                assert fail_count == num_failing_tcs, (
                    f"Mismatch for bug_idx {bug_idx}: "
                    f"tc_info fail_count ({fail_count}) != num_failing_tcs ({num_failing_tcs})"
                )
                assert pass_count == num_passing_tcs, (
                    f"Mismatch for bug_idx {bug_idx}: "
                    f"tc_info pass_count ({pass_count}) != num_passing_tcs ({num_passing_tcs})"
                )
            else:
                raise AssertionError(
                    f"No matching tc_info rows found for bug_idx {bug_idx}."
                )

        print(f"[stage03-VAL05] {len(bug_info_res)} buggy versions with prerequisites=TRUE have valid failing and passing test case counts")

    def val06(self):
        """
        [stage03] val06: Validate that all lines_executed_by_failing_tc.json and line2function.json file
            are available for all buggy versions resulting from prerequisite data preparation
        """

        version_list = self.db.read(
            "bug_info",
            columns="version",
            conditions={
                "subject": self.subject_name,
                "experiment_name": self.experiment_name,
                "prerequisites": True
            }
        )

        prerequisite_dir = out_dir / self.subject_name / "prerequisite_data"
        for version in version_list:
            version_name = version[0]
            version_dir = prerequisite_dir / version_name

            # Validate lines_executed_by_failing_tc.json
            lines_executed_by_failing_tc_file = version_dir / "coverage_info" / "lines_executed_by_failing_tc.json"
            assert lines_executed_by_failing_tc_file.exists(), f"lines_executed_by_failing_tc.json not found for {version_name}"

            # Validate line2function.json
            line2function_file = version_dir / "line2function_info" / "line2function.json"
            assert line2function_file.exists(), f"line2function.json not found for {version_name}"
        
        print(f"[stage03-VAL06] {len(version_list)} buggy versions with prerequisites=TRUE have valid lines_executed_by_failing_tc.json and line2function.json files")

    def val07(self):
        """
        [stage03] Validate the following for all tc_info with tc_result one of the ['fail', 'pass', 'cct']
            and bug_idx one of the bug_idx in bug_info with subject, experiment_name, and prerequisites IS TRUE:
            1. The length of branch_cov_bit_seq is equal to the length of first branch_cov_bit_seq of the tc_info.
        """

        # Step 1: Fetch all bug_idx and required columns from bug_info
        columns = ["b.bug_idx", "b.num_failing_tcs", "b.num_passing_tcs", "b.num_ccts"]
        col_str = ", ".join(columns)
        spechal_str = f"""
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.prerequisites IS TRUE
        """

        bug_info_list = self.db.read(
            "bug_info b",
            columns=col_str,
            special=spechal_str
        )

        print(f">> Total {len(bug_info_list)} bug_idx found for validation")
        for bug_info in bug_info_list:
            bug_idx, fail_cnt, pass_cnt, cct_cnt = bug_info
            total_tc_cnt = fail_cnt + pass_cnt + cct_cnt

            columns = [
                "t.bug_idx", "t.tc_idx", "t.tc_result",
                "t.branch_cov_bit_seq"
            ]
            col_str = ", ".join(columns)
            tc_info_list = self.db.read(
                "tc_info t",
                columns=col_str,
                conditions={
                    "bug_idx": bug_idx,
                },
                special="ORDER BY t.tc_idx ASC"
            )

            branch_cov_length = len(tc_info_list[0][3])
            for tc_info in tc_info_list:
                tBug_idx, tc_idx, tc_result, branch_cov_bit_seq = tc_info
                if tc_result not in ["fail", "pass", "cct"]:
                    continue

                # Validate the lengths of features
                # if len(branch_cov_bit_seq) != branch_cov_length:
                #     print(f"{len(branch_cov_bit_seq)} != {branch_cov_length}")
                #     print(f"bug_idx: {bug_idx}, tc_idx: {tc_idx}, tc_result: {tc_result}")
                assert len(branch_cov_bit_seq) == branch_cov_length, f"Length of branch_cov_bit_seq is not equal to branch_cov_length for bug_idx {bug_idx}"

        print(f"[stage06-VAL07] {len(bug_info_list)} buggy versions have valid branch_cov_bit_seq length for all tc in tc_info")

    def val08(self):
        """
        [stage04] val07: Validate the following for all bug_idx in bug_info with sbfl IS TRUE:
            1. Columns ep, np, ef, nf, cct_ep, and cct_np in line_info are not NULL.
            2. ep + np = num_passing_tcs in bug_info.
            3. ef + nf = num_failing_tcs in bug_info.
            4. cct_ep + cct_np = num_ccts in bug_info.
        """

        # Step 1: Fetch all bug_idx and required columns from bug_info
        columns = ["b.bug_idx", "b.num_passing_tcs", "b.num_failing_tcs", "b.num_ccts"]
        col_str = ", ".join(columns)

        special_str = f"""
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.sbfl IS TRUE
        """

        bug_info_res = self.db.read(
            "bug_info b",
            columns=col_str,
            special=special_str
        )

        # Map bug_info data by bug_idx for quick validation
        bug_info_map = {
            row[0]: {
                "num_passing_tcs": row[1],
                "num_failing_tcs": row[2],
                "num_ccts": row[3]
            }
            for row in bug_info_res
        }

        # Step 2: Fetch line_info data for the relevant bug_idx
        columns = ["l.bug_idx", "l.line_idx", "l.ep", "l.np", "l.ef", "l.nf", "l.cct_ep", "l.cct_np"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON l.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.sbfl IS TRUE
        """

        line_info_res = self.db.read(
            "line_info l",
            columns=col_str,
            special=special_str
        )

        # Step 3: Validate columns and make line_info map values by bug_idx, line_idx
        line_info_map = {}
        for row in line_info_res:
            bug_idx = row[0]
            line_line_idx = row[1]
            ep, np, ef, nf, cct_ep, cct_np = row[2:]

            # Ensure no column is NULL
            assert ep is not None, f"ep is NULL for bug_idx {bug_idx}"
            assert np is not None, f"np is NULL for bug_idx {bug_idx}"
            assert ef is not None, f"ef is NULL for bug_idx {bug_idx}"
            assert nf is not None, f"nf is NULL for bug_idx {bug_idx}"
            assert cct_ep is not None, f"cct_ep is NULL for bug_idx {bug_idx}"
            assert cct_np is not None, f"cct_np is NULL for bug_idx {bug_idx}"

            # Store the values in line_info_map
            if bug_idx not in line_info_map:
                line_info_map[bug_idx] = {}
            line_info_map[bug_idx][line_line_idx] = {
                "ep": ep, "np": np, "ef": ef, "nf": nf, "cct_ep": cct_ep, "cct_np": cct_np
            }
            

        # Step 4: Validate line_info data against bug_info data
        for bug_idx, lines_data in line_info_map.items():
            for line_idx, line_data in lines_data.items():
                assert line_data["ep"] + line_data["np"] == bug_info_map[bug_idx]["num_passing_tcs"], (
                    f"Mismatch for bug_idx {bug_idx}, line_idx {line_idx}: "
                    f"ep + np ({line_data['ep']} + {line_data['np']}) != num_passing_tcs ({bug_info_map[bug_idx]['num_passing_tcs']})"
                )

                assert line_data["ef"] + line_data["nf"] == bug_info_map[bug_idx]["num_failing_tcs"], (
                    f"Mismatch for bug_idx {bug_idx}, line_idx {line_idx}: "
                    f"ef + nf ({line_data['ef']} + {line_data['nf']}) != num_failing_tcs ({bug_info_map[bug_idx]['num_failing_tcs']})"
                )

                assert line_data["cct_ep"] + line_data["cct_np"] == bug_info_map[bug_idx]["num_ccts"], (
                    f"Mismatch for bug_idx {bug_idx}, line_idx {line_idx}: "
                    f"cct_ep + cct_np ({line_data['cct_ep']} + {line_data['cct_np']}) != num_ccts ({bug_info_map[bug_idx]['num_ccts']})"
                )

        print(f"[stage04-VAL08] {len(bug_info_res)} buggy versions with sbfl=TRUE have valid sbfl feature data in line_info")

    def val09(self):
        """
        [stage05] val08: Validate the following columns in line_info table for all bug_idx in bug_info with mbfl IS TRUE:
            1. selected_for_mbfl is TRUE
        """
        # Step 1: Fetch line_info data for buggy line for the relevant bug_idx
        columns = ["l.bug_idx", "l.selected_for_mbfl"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON l.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.mbfl IS TRUE
            AND l.is_buggy_line IS TRUE
        """

        line_info_res = self.db.read(
            "line_info l",
            columns=col_str,
            special=special_str
        )

        # Step 2: Validate the values
        for row in line_info_res:
            bug_idx = row[0]
            selected_for_mbfl = row[1]

            # assert for_sbfl_ranked_mbfl_asc is True, f"for_sbfl_ranked_mbfl_asc is not TRUE for bug_idx {bug_idx}"
            assert selected_for_mbfl is True, f"selected_for_mbfl is not TRUE for bug_idx {bug_idx}"

        print(f"[stage05-VAL09] {len(line_info_res)} buggy lines with mbfl=TRUE is targetd for all types (sbfl asc, desc, and random mbfl) of mbfl extraction method")

    def val10(self):
        """
        [stage05] val09: Validate number of mutations generated on buggy line is greater than 0 for all bug_idx in bug_info with mbfl IS TRUE
        """
        columns = ["m.bug_idx", "COUNT(m.mutant_idx)"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON m.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.buggy_line_idx = m.line_idx
            AND b.mbfl IS TRUE
            AND m.is_for_test IS TRUE
            GROUP BY m.bug_idx
        """
        
        res = self.db.read(
            "mutation_info m",
            columns=col_str,
            special=special_str
        )

        for row in res:
            assert row[1] > 0, f"Number of mutations is not greater than 0 for bug_idx {row[0]}"

        print(f"[stage05-VAL10] {len(res)} buggy lines with mbfl=TRUE have greater than 0 mutations generated")

    def val11(self):
        """
        [stage05] val10: Validate the following for all bug_idx in bug_info with mbfl IS TRUE:
            1. Columns f2p, p2f, f2f, p2p, p2f_cct, and p2p_cct in mutation_info are not NULL.
            2. f2p + f2f = num_failing_tcs in bug_info.
            3. p2f + p2p = num_passing_tcs in bug_info.
            4. p2f_cct + p2p_cct = num_ccts in bug_info.
        """

        # Step 1: Fetch all bug_idx and required columns from bug_info
        columns = ["b.bug_idx", "b.num_passing_tcs", "b.num_failing_tcs", "b.num_ccts"]
        col_str = ", ".join(columns)

        special_str = f"""
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.mbfl IS TRUE
        """

        bug_info_res = self.db.read(
            "bug_info b",
            columns=col_str,
            special=special_str
        )

        # Map bug_info data by bug_idx for quick validation
        bug_info_map = {
            row[0]: {
                "num_passing_tcs": row[1],
                "num_failing_tcs": row[2],
                "num_ccts": row[3]
            }
            for row in bug_info_res
        }

        # Step 2: Fetch mutation_info data for the relevant bug_idx
        columns = ["m.bug_idx", "m.f2p", "m.p2f", "m.f2f", "m.p2p", "m.p2f_cct", "m.p2p_cct"]
        col_str = ", ".join(columns)

        special_str = f"""
            INNER JOIN bug_info b ON m.bug_idx = b.bug_idx
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.mbfl IS TRUE
            AND m.is_for_test IS TRUE
            AND m.build_result IS TRUE
        """

        mutation_info_res = self.db.read(
            "mutation_info m",
            columns=col_str,
            special=special_str
        )

        # Step 3: Validate columns and make mutation_info map values by bug_idx
        mutation_info_map = {}
        for row in mutation_info_res:
            bug_idx = row[0]
            f2p, p2f, f2f, p2p, p2f_cct, p2p_cct = row[1:]

            # Ensure no column is NULL
            assert f2p is not None, f"f2p is NULL for bug_idx {bug_idx}"
            assert p2f is not None, f"p2f is NULL for bug_idx {bug_idx}"
            assert f2f is not None, f"f2f is NULL for bug_idx {bug_idx}"
            assert p2p is not None, f"p2p is NULL for bug_idx {bug_idx}"
            assert p2f_cct is not None, f"p2f_cct is NULL for bug_idx {bug_idx}"
            assert p2p_cct is not None, f"p2p_cct is NULL for bug_idx {bug_idx}"

            # Store the values in mutation_info_map
            if bug_idx not in mutation_info_map:
                mutation_info_map[bug_idx] = []
            mutation_info_map[bug_idx].append({
                "f2p": f2p, "p2f": p2f, "f2f": f2f, "p2p": p2p, "p2f_cct": p2f_cct, "p2p_cct": p2p_cct
            })

        # Step 4: Validate mutation_info data against bug_info data
        for bug_idx, mutations_data in mutation_info_map.items():
            for mutation_data in mutations_data:
                assert mutation_data["f2p"] + mutation_data["f2f"] == bug_info_map[bug_idx]["num_failing_tcs"], (
                    f"Mismatch for bug_idx {bug_idx}: "
                    f"f2p + f2f ({mutation_data['f2p']} + {mutation_data['f2f']}) != num_failing_tcs ({bug_info_map[bug_idx]['num_failing_tcs']})"
                )

                assert mutation_data["p2f"] + mutation_data["p2p"] == bug_info_map[bug_idx]["num_passing_tcs"], (
                    f"Mismatch for bug_idx {bug_idx}: "
                    f"p2f + p2p ({mutation_data['p2f']} + {mutation_data['p2p']}) != num_passing_tcs ({bug_info_map[bug_idx]['num_passing_tcs']})"
                )

                assert mutation_data["p2f_cct"] + mutation_data["p2p_cct"] == bug_info_map[bug_idx]["num_ccts"], (
                    f"Mismatch for bug_idx {bug_idx}: "
                    f"p2f_cct + p2p_cct ({mutation_data['p2f_cct']} + {mutation_data['p2p_cct']}) != num_ccts ({bug_info_map[bug_idx]['num_ccts']})"
                )

        print(f"[stage05-VAL11] {len(bug_info_res)} buggy versions with mbfl=TRUE have valid mbfl feature data in mutation_info")

    def val12(self):
        """
        [stage05] val11: Validate the following for all mutation_info with
            bug_idx one of the bug_idx in bug_info with subject, experiment_name, and mbfl IS TRUE:
            1. the lengths of following features equals the total number of tc which is fail+pass+cct
                - f2p_tc_cov_bit_seq, p2f_tc_cov_bit_seq, f2f_tc_cov_bit_seq, p2p_tc_cov_bit_seq, p2f_cct_tc_cov_bit_seq, p2p_cct_tc_cov_bit_seq
            2. the sum of all "1" in the features equals the total number of tc which is fail+pass+cct
        """

        # Step 1: Fetch all bug_idx and required columns from bug_info
        columns = ["b.bug_idx", "b.num_failing_tcs", "b.num_passing_tcs", "b.num_ccts"]
        col_str = ", ".join(columns)
        spechal_str = f"""
            WHERE b.subject = '{self.subject_name}'
            AND b.experiment_name = '{self.experiment_name}'
            AND b.mbfl IS TRUE
        """

        bug_info_list = self.db.read(
            "bug_info b",
            columns=col_str,
            special=spechal_str
        )

        print(f">> Total {len(bug_info_list)} bug_idx found for validation")
        for bug_info in bug_info_list:
            bug_idx, fail_cnt, pass_cnt, cct_cnt = bug_info
            total_tc_cnt = fail_cnt + pass_cnt + cct_cnt

            columns = [
                "m.bug_idx", "m.f2p_tc_bit_seq", "m.p2f_tc_bit_seq", "m.f2f_tc_bit_seq",
                "m.p2p_tc_bit_seq", "m.p2f_cct_tc_bit_seq", "m.p2p_cct_tc_bit_seq"
            ]
            col_str = ", ".join(columns)

            mutation_info_list = self.db.read(
                "mutation_info m",
                columns=col_str,
                conditions={
                    "bug_idx": bug_idx,
                    "is_for_test": True,
                    "build_result": True
                }
            )

            for mutation_info in mutation_info_list:
                mBug_idx, f2p, p2f, f2f, p2p, p2f_cct, p2p_cct = mutation_info

                # Validate the lengths of features
                assert len(f2p) == total_tc_cnt, f"Length of f2p_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"
                assert len(p2f) == total_tc_cnt, f"Length of p2f_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"
                assert len(f2f) == total_tc_cnt, f"Length of f2f_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"
                assert len(p2p) == total_tc_cnt, f"Length of p2p_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"
                assert len(p2f_cct) == total_tc_cnt, f"Length of p2f_cct_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"
                assert len(p2p_cct) == total_tc_cnt, f"Length of p2p_cct_tc_bit_seq is not equal to total_tc_cnt for bug_idx {bug_idx}"

                # Validate the sum of all "1" in the features
                f2p_cnt = f2p.count("1")
                p2f_cnt = p2f.count("1")
                f2f_cnt = f2f.count("1")
                p2p_cnt = p2p.count("1")
                p2f_cct_cnt = p2f_cct.count("1")
                p2p_cct_cnt = p2p_cct.count("1")

                assert f2p_cnt + f2f_cnt == fail_cnt, f"Sum of '1' in f2p and f2f is not equal to fail_cnt for bug_idx {bug_idx}"
                assert p2f_cnt + p2p_cnt == pass_cnt, f"Sum of '1' in p2f and p2p is not equal to pass_cnt for bug_idx {bug_idx}"
                assert p2f_cct_cnt + p2p_cct_cnt == cct_cnt, f"Sum of '1' in p2f_cct and p2p_cct is not equal to cct_cnt for bug_idx {bug_idx}"

                all_cnt = f2p_cnt + p2f_cnt + f2f_cnt + p2p_cnt + p2f_cct_cnt + p2p_cct_cnt
                assert all_cnt == total_tc_cnt, f"Sum of all '1' in the features is not equal to total_tc_cnt for bug_idx {bug_idx}"
        
        print(f"[stage06-VAL12] {len(bug_info_list)} buggy versions with mbfl=TRUE have valid mbfl feature data in mutation_info")



    # ++++++++++++++++++++++++++++++++
    # ++++ VALIDATE FL FEATURES ++++
    # ++++++++++++++++++++++++++++++++
    def validate_fl_features(self):

        bug_version_mutation_info_file = self.set_dir / "bug_version_mutation_info.csv"
        assert bug_version_mutation_info_file.exists(), f"Bug version mutation info file {bug_version_mutation_info_file} does not exist"

        bugs = {}
        with open(bug_version_mutation_info_file, "r") as f:
            lines = f.readlines()
            for line in lines[2:]:
                line = line.strip()
                info = line.split(",")
                bug_id = info[0]
                assert bug_id not in bugs, f"Duplicate bug id {bug_id}"
                bugs[bug_id] = line

        bug_keys = list(bugs.keys())
        bug_keys = sorted(bug_keys, key=sort_bug_id)

        for idx, bug in enumerate(bug_keys):
            print(f"Validating FL features for {bug} ({idx+1}/{len(bugs)})")
            fl_features_file = self.set_dir / f"FL_features_per_bug_version/{bug}.fl_features.csv"
            assert fl_features_file.exists(), f"FL features file {fl_features_file} does not exist"

            # VALIDATE: that there is only one row with "bug" column as 1
            self.check_one_buggy_line(fl_features_file)
            print(f"\t VAL01: One buggy line check passed")




            failing_tcs_file = self.set_dir / f"test_case_info_per_bug_version/{bug}/failing_tcs.txt"
            assert failing_tcs_file.exists(), f"Failing test cases file {failing_tcs_file} does not exist"
            passing_tcs_file = self.set_dir / f"test_case_info_per_bug_version/{bug}/passing_tcs.txt"
            assert passing_tcs_file.exists(), f"Passing test cases file {passing_tcs_file} does not exist"

            failing_tcs_list = get_tc_list(failing_tcs_file)
            passing_tcs_list = get_tc_list(passing_tcs_file)
            num_utilized_tcs = len(failing_tcs_list) + len(passing_tcs_list)

            # VALIDATE: that the ep, ef, np, nf values from fl_features_file (csv) add up to num_utilized_tcs
            self.check_spectrum2num_utilized_tcs(fl_features_file, num_utilized_tcs)
            print(f"\t VAL02: Spectrum to number of utilized test cases check passed")




            buggy_line_key_file = self.set_dir / f"buggy_line_key_per_bug_version/{bug}.buggy_line_key.txt"
            assert buggy_line_key_file.exists(), f"Buggy line key file {buggy_line_key_file} does not exist"

            with open(buggy_line_key_file, "r") as f:
                buggy_line_key = f.readline().strip()
            
            postprocessed_coverage_file = self.set_dir / f"postprocessed_coverage_per_bug_version/{bug}.cov_data.csv"
            assert postprocessed_coverage_file.exists(), f"Postprocessed coverage file {postprocessed_coverage_file} does not exist"

            # VALIDATE: that all failing tcs execute the buggy line
            res = self.check_failing_tcs(postprocessed_coverage_file, failing_tcs_list, buggy_line_key)
            assert res, f"Failing test cases do not execute the buggy line in {postprocessed_coverage_file}"
            print(f"\t VAL03: Failing test cases execute buggy line check passed")




            num_failing_tcs = len(failing_tcs_list)
            fl_features_file_with_susp = self.set_dir / f"FL_features_per_bug_version_with_susp_scores/{bug}.fl_features_with_susp_scores.csv"
            assert fl_features_file_with_susp.exists(), f"FL features file with suspicious scores {fl_features_file_with_susp} does not exist"
            
            # VALIDATE: that with mutation features from fl_features_file,
            # the met and muse score from fl_features_file_with_susp can be derived
            self.check_met_muse(fl_features_file, fl_features_file_with_susp, num_failing_tcs)
            print(f"\t VAL04: MET and MUSE score check passed")


            bug_info = bugs[bug]
            target_code_file_name = self.get_target_code_file_name(bug_info)
            buggy_code_file = self.set_dir / f"buggy_code_file_per_bug_version/{bug}/{target_code_file_name}"
            assert buggy_code_file.exists(), f"Buggy code file {buggy_code_file} does not exist"

            # VALIDATE: that the mutated code exists in the buggy code file
            self.check_mutated_code(buggy_code_file, bug_info, buggy_line_key)
            print(f"\t VAL05: Mutated code check passed")

            # if idx == 7:
            #     break

        print(f"All {len(bugs)} bugs have been validated successfully")
    
    def check_mutated_code(self, buggy_code_file, bug_info, buggy_line_key):
        written_buggy_lineno = int(buggy_line_key.split("#")[-1])

        info = bug_info.split(",")
        bug_id = info[0]
        target_code_file_name = info[1]
        buggy_code_file_name = info[2]
        
        mut_op = info[3]
        if mut_op == "":
            return

        buggy_lineno = None
        if self.subject_name == "jsoncpp":
            buggy_lineno = int(info[2])
        else:
            buggy_lineno = int(info[4])
        assert written_buggy_lineno == buggy_lineno, f"Buggy line number {written_buggy_lineno} does not match with buggy line number {buggy_lineno}"

        before_mutation = None
        after_mutation = None
        if self.subject_name == "jsoncpp":
            before_mutation = info[4]
            after_mutation = info[5]
        else:
            before_mutation = info[8]
            after_mutation = info[13]
            
        # print(f"bug_id: {bug_id}")
        # print(f"target_code_file_name: {target_code_file_name}")
        # print(f"line_no: {buggy_lineno}")
        # print(f"before_mutation: {before_mutation}")
        # print(f"after_mutation: {after_mutation}")

        with open(buggy_code_file, "r", encoding="utf-8", errors="ignore") as f: # 2024-08-19
            lines = f.readlines()
            buggy_line = lines[buggy_lineno-1].strip()
            assert after_mutation in buggy_line, f"Mutated code {after_mutation} not found in buggy code file {buggy_code_file}"





    
    def get_target_code_file_name(self, bug_info):
        info = bug_info.split(",")
        bug_id = info[0]
        target_code_file_name = info[1]
        return target_code_file_name
    
    def check_met_muse(self, fl_features_file, fl_features_file_with_susp, num_failing_tcs):
        max_mutants = self.get_max_mutants_from_feature_file(fl_features_file)
        mutant_keys = get_mutant_keys_as_pairs(max_mutants)
        tot_failed_TCs, total_p2f, total_f2p = self.measure_required_info(fl_features_file, mutant_keys)

        # score format: key: formula_key, value: score
        scores = {}
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                met_score = measure_metallaxis(row, mutant_keys)
                muse_data = measure_muse(row, total_p2f, total_f2p, mutant_keys)
                muse_score = muse_data[muse_key]
                scores[row["key"]] = {
                    "met": met_score,
                    "muse": muse_score
                }

        with open(fl_features_file_with_susp, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["key"]
                met_score = float(row[met_key])
                muse_score = float(row[muse_key])
                assert scores[key]["met"] == met_score, f"MET score for {key} does not match"
                assert scores[key]["muse"] == muse_score, f"MUSE score for {key} does not match"
    
    def measure_required_info(self, fl_features_file, mutant_keys):
        tot_failed_TCs = self.get_tot_failed_TCs(fl_features_file)

        total_p2f = 0
        total_f2p = 0
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for p2f_m, f2p_m in mutant_keys:
                    if row[p2f_m] == "-1" and row[f2p_m] == "-1":
                        continue
                    p2f = int(row[p2f_m])
                    f2p = int(row[f2p_m])
                    total_p2f += p2f
                    total_f2p += f2p
        
        return tot_failed_TCs, total_p2f, total_f2p
    
    def get_tot_failed_TCs(self, fl_features_file):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                num_failing_tcs = int(row["# of totfailed_TCs"])
                return num_failing_tcs
    
    def get_max_mutants_from_feature_file(self, fl_features_file):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                max_mutants = int(row["# of mutants"])
                return max_mutants
        
    
    def check_spectrum2num_utilized_tcs(self, fl_features_file, num_utilized_tcs):
        with open(fl_features_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ep = int(row["ep"])
                ef = int(row["ef"])
                np = int(row["np"])
                nf = int(row["nf"])
                assert ep + ef + np + nf == num_utilized_tcs, f"Sum of ep, ef, np, nf is not equal to {num_utilized_tcs} in {fl_features_file}"
    
