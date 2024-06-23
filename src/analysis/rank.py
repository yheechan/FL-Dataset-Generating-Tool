
import csv

from lib.experiment import Experiment
from lib.utils import *
from analysis.rank_utils import *
from analysis.analyze import Analyze
from analysis.individual import Individual
from lib.susp_score_formula import sbfl_formulas


class Rank(Analyze):
    def __init__(self, subject_name, set_name, output_csv):
        super().__init__(subject_name, set_name, output_csv)
        self.experiment = Experiment()

    # +++++++++++++++++++++++
    # ++++++ Rank MBFL ++++++
    # +++++++++++++++++++++++
    def rank_mbfl_features(self):
        self.max_mutants = self.experiment.experiment_config["max_mutants"]
        self.mutant_keys = get_mutant_keys(self.max_mutants)

        self.bugs_list = []
        self.acc5_met = []
        self.acc10_met = []
        self.acc5_muse = []
        self.acc10_muse = []

        for idx, version_dir in enumerate(self.individual_list):
            print(f"\n{idx+1}/{len(self.individual_list)}: {version_dir.name}")

            individual = Individual(self.subject_name, self.set_name, version_dir.name)

            mbfl_features_csv_file = individual.dir_path / "mbfl_features.csv"
            assert mbfl_features_csv_file.exists(), f"MBFL features file {mbfl_features_csv_file} does not exist"

            buggy_line_key = get_buggy_line_key_from_data(individual.dir_path)
            lines_executed_by_failing_tcs = get_lines_executed_by_failing_tcs_from_data(individual.dir_path)

            assert buggy_line_key in lines_executed_by_failing_tcs, f"buggy_line_key {buggy_line_key} not in lines_executed_by_failing_tcs"

            mutation_testing_result_data = get_mutation_testing_results_form_data(individual.dir_path, buggy_line_key)

            ranks = {}
            for mbfl_formula in mbfl_formulas:
                rank_data = get_mbfl_rank_at_method_level(
                    mbfl_features_csv_file,
                    buggy_line_key,
                    mbfl_formula,
                    self.mutant_keys
                )
                ranks[mbfl_formula] = rank_data
            
            print(f"\tmet rank: {ranks[met_key][bug_rank_key]}")
            print(f"\tmuse rank: {ranks[muse_key][bug_rank_key]}")

            self.append_mbfl_results(
                individual.name,
                buggy_line_key,
                individual.failing_tcs_list,
                lines_executed_by_failing_tcs,
                mutation_testing_result_data,
                ranks
            )
        
        self.print_mbfl_accuracy()
        self.write_rank_results()
    
    def append_mbfl_results(
        self, bug_name, buggy_line_key, failing_tcs,
        lines_executed_by_failing_tcs, mutation_testing_result_data, ranks
    ):
        
        self.bugs_list.append({
            'bug_name': bug_name,
            'buggy_line_key': buggy_line_key,

            '# of failing Tcs': len(failing_tcs),

            '# of lines executed by failing TCs': len(lines_executed_by_failing_tcs),
            
            '# of mutants': mutation_testing_result_data['# mutants'],
            '# of uncompilable mutants': mutation_testing_result_data['# uncompilable mutants'],
            '# of mutans on buggy line': mutation_testing_result_data['# mutans on buggy line'],
            '# of uncompilable mutants on buggy line': mutation_testing_result_data['# uncompilable mutants on buggy line'],
            '# of compilable mutants on buggy line': mutation_testing_result_data['# compilable mutants on buggy line'],

            'total p2f (all mutants)': mutation_testing_result_data['total_p2f'],
            'total f2p (all mutants)': mutation_testing_result_data['total_f2p'],

            '# of functions': ranks[met_key]['# of functions'],

            '# of function with same highest met score': ranks[met_key]['# of functions with same highest score'],
            'met score of highest rank': ranks[met_key]['score of highest rank'],
            'rank of buggy function (function level) (met)': ranks[met_key]['rank of buggy function (function level)'],
            'met score of buggy function': ranks[met_key]['score of buggy function'],

            '# of function with same highest muse score': ranks[muse_key]['# of functions with same highest score'],
            'muse score of highest rank': ranks[muse_key]['score of highest rank'],
            'rank of buggy function (function level) (muse)': ranks[muse_key]['rank of buggy function (function level)'],
            'muse score of buggy function': ranks[muse_key]['score of buggy function'],
        })

        if ranks[met_key][bug_rank_key] <= 5:
            self.acc5_met.append(bug_name)
        if ranks[met_key][bug_rank_key] <= 10:
            self.acc10_met.append(bug_name)
        if ranks[muse_key][bug_rank_key] <= 5:
            self.acc5_muse.append(bug_name)
        if ranks[muse_key][bug_rank_key] <= 10:
            self.acc10_muse.append(bug_name)
    
    def print_mbfl_accuracy(self):
        print("\n\n")
        print(f"met acc@5: {len(self.acc5_met)}")
        print(f"met acc@5 perc: {len(self.acc5_met)/len(self.bugs_list)}")
        print(f"met acc@10: {len(self.acc10_met)}")
        print(f"met acc@10 perc: {len(self.acc10_met)/len(self.bugs_list)}")

        print("\n")
        print(f"muse acc@5: {len(self.acc5_muse)}")
        print(f"muse acc@5 perc: {len(self.acc5_muse)/len(self.bugs_list)}")
        print(f"muse acc@10: {len(self.acc10_muse)}")
        print(f"muse acc@10 perc: {len(self.acc10_muse)/len(self.bugs_list)}")

    def write_rank_results(self):
        with open(self.output_csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=self.bugs_list[0].keys())
            writer.writeheader()
            for bug in self.bugs_list:
                writer.writerow(bug)

    # +++++++++++++++++++++++
    # ++++++ Rank SBFL ++++++
    # +++++++++++++++++++++++
    def rank_sbfl_features(self):
        self.bugs_list = []
        self.accuracy = {
            "acc@5": {
                "Binary": [],
                "GP13": [],
                "Jaccard": [],
                "Naish1": [],
                "Naish2": [],
                "Ochiai": [],
                "Russel+Rao": [],
                "Wong1": []
            },
            "acc@10": {
                "Binary": [],
                "GP13": [],
                "Jaccard": [],
                "Naish1": [],
                "Naish2": [],
                "Ochiai": [],
                "Russel+Rao": [],
                "Wong1": []
            }
        }

        cnt = 0
        for idx, version_dir in enumerate(self.individual_list):
            print(f"\n{idx+1}/{len(self.individual_list)}: {version_dir.name}")
            individual = Individual(self.subject_name, self.set_name, version_dir.name)

            buggy_line_key = get_buggy_line_key_from_data(individual.dir_path)
            key_info = buggy_line_key.split("#")
            bug_target_file = key_info[0].strip().split("/")[-1]
            bug_funciton_name = key_info[1].strip()
            bug_line_num = int(key_info[2].strip())

            cnt += 1

            ranks = {}
            for sbfl_formula in sbfl_formulas:
                rank_data = get_sbfl_rank_at_method_level(
                    individual.dir_path / "sbfl_features.csv",
                    buggy_line_key, sbfl_formula
                )
                ranks[sbfl_formula] = rank_data
            
            write_data = {
                'bug_name': individual.name,
                # 'bug_target_file': bug_target_file,
                # 'bug_function_name': bug_function_name,
                'key': buggy_line_key
            }

            for sbfl_formula in sbfl_formulas:
                for key, value in ranks[sbfl_formula].items():
                    write_data[key] = value

            self.bugs_list.append(write_data)

            for key in self.accuracy.keys():
                for formula in sbfl_formulas:
                    bug_rank_key = f"rank of buggy function ({formula})"
                    thresh = 5 if key == "acc@5" else 10
                    if ranks[formula][bug_rank_key] <= thresh:
                        self.accuracy[key][formula].append(individual.name)
        
        self.print_sbfl_accuracy()
        self.write_sbfl_rank_results()
    
    def print_sbfl_accuracy(self):
        print("\n\n")
        for key, value in self.accuracy.items():
            for formula, bugs in value.items():
                print(f"{key} {formula}: {len(bugs)}")
                print(f"{key} {formula} perc: {len(bugs)/len(self.bugs_list)}")

    def write_sbfl_rank_results(self):
        with open(self.output_csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=self.bugs_list[0].keys())
            writer.writeheader()
            for bug in self.bugs_list:
                writer.writerow(bug)
