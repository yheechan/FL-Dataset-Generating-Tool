
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
    def rank_mbfl_features(self, trialName=None, noCCTs=False):
        self.max_mutants = self.experiment.experiment_config["max_mutants"]
        self.mutant_keys = get_mutant_keys(self.max_mutants)

        self.bugs_list = []
        self.acc5_met = []
        self.acc10_met = []
        self.acc5_muse = []
        self.acc10_muse = []

        self.acc_muse = []
        self.acc_met = []

        mbfl_feature_type = "mbfl_features.csv"
        if noCCTs:
            mbfl_feature_type = "mbfl_features_noCCTs.csv"
        print(f"rank on {mbfl_feature_type}")

        for idx, version_dir in enumerate(self.individual_list):
            print(f"\n{idx+1}/{len(self.individual_list)}: {version_dir.name}")

            individual = Individual(self.subject_name, self.set_name, version_dir.name)

            mbfl_features_csv_file = individual.dir_path / mbfl_feature_type
            assert mbfl_features_csv_file.exists(), f"MBFL features file {mbfl_features_csv_file} does not exist"

            buggy_line_key = get_buggy_line_key_from_data(individual.dir_path)
            lines_executed_by_failing_tcs = get_lines_executed_by_failing_tcs_from_data(individual.dir_path)
            funcs_executed_by_failing_tcs = get_file_func_pair_executed_by_failing_tcs(lines_executed_by_failing_tcs)
            number_of_funcs_executed_by_failing_tcs = len(funcs_executed_by_failing_tcs)
            print(f"\tnumber of func. executed by failing tcs: {number_of_funcs_executed_by_failing_tcs}")

            assert buggy_line_key in lines_executed_by_failing_tcs, f"buggy_line_key {buggy_line_key} not in lines_executed_by_failing_tcs"

            mutation_testing_result_data = get_mutation_testing_results_form_data(individual.dir_path, buggy_line_key, trialName)

            ranks = {}
            for mbfl_formula in mbfl_formulas:
                rank_data = get_mbfl_rank_at_method_level(
                    mbfl_features_csv_file,
                    buggy_line_key,
                    mbfl_formula,
                    self.mutant_keys,
                    funcs_executed_by_failing_tcs
                )
                ranks[mbfl_formula] = rank_data
    
            print(f"\tmet rank: {ranks[met_key][bug_rank_key]}")
            print(f"\tmuse rank: {ranks[muse_key][bug_rank_key]}")
            
            director = f"rank of buggy function among functions executed by failing tcs ({met_key})"
            print(f"\tmet rank among func. executed by failing tcs: {ranks[met_key][director]}")

            director = f"rank of buggy function among functions executed by failing tcs ({muse_key})"
            print(f"\tmuse rank among func. executed by failing tcs: {ranks[muse_key][director]}")

            self.append_mbfl_results(
                individual.name,
                buggy_line_key,
                individual.failing_tcs_list,
                lines_executed_by_failing_tcs,
                mutation_testing_result_data,
                ranks,
                number_of_funcs_executed_by_failing_tcs
            )
        
        self.print_mbfl_accuracy()
        self.write_rank_results()
    
    def append_mbfl_results(
        self, bug_name, buggy_line_key, failing_tcs,
        lines_executed_by_failing_tcs, mutation_testing_result_data, ranks,
        number_of_funcs_executed_by_failing_tcs
    ):
        print(f"\tnumber of func. executed by failing tcs: {number_of_funcs_executed_by_failing_tcs}")

        met_director = f"rank of buggy function among functions executed by failing tcs ({met_key})"
        met_rank = ranks[met_key][met_director]
        met_acc = (met_rank / number_of_funcs_executed_by_failing_tcs) * 100
        self.acc_met.append(met_acc)
        print(f"\tmet acc: {met_acc}")

        muse_director = f"rank of buggy function among functions executed by failing tcs ({muse_key})"
        muse_rank = ranks[muse_key][muse_director]
        muse_acc = (muse_rank / number_of_funcs_executed_by_failing_tcs) * 100
        self.acc_muse.append(muse_acc)
        print(f"\tmuse acc: {muse_acc}")
        
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
            "# of func. executed by failing TCs": number_of_funcs_executed_by_failing_tcs,

            '# of function with same highest met score': ranks[met_key]['# of functions with same highest score'],
            'met score of highest rank': ranks[met_key]['score of highest rank'],
            'rank of buggy function (function level) (met)': ranks[met_key]['rank of buggy function (function level)'],
            'met score of buggy function': ranks[met_key]['score of buggy function'],
            "rank of buggy function among func. executed by failing tcs (met)": ranks[met_key][met_director],
            "met accuracy among func. executed by failing tcs": met_acc,

            '# of function with same highest muse score': ranks[muse_key]['# of functions with same highest score'],
            'muse score of highest rank': ranks[muse_key]['score of highest rank'],
            'rank of buggy function (function level) (muse)': ranks[muse_key]['rank of buggy function (function level)'],
            'muse score of buggy function': ranks[muse_key]['score of buggy function'],
            "rank of buggy function among func. executed by failing tcs (muse)": ranks[muse_key][muse_director],
            "muse accuracy among func. executed by failing tcs": muse_acc
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
        content = "\n\n"
        content += f"met acc@5: {len(self.acc5_met)}\n"
        content += f"met acc@5 perc: {len(self.acc5_met)/len(self.bugs_list)}\n"
        content += f"met acc@10: {len(self.acc10_met)}\n"
        content += f"met acc@10 perc: {len(self.acc10_met)/len(self.bugs_list)}\n"
        content += f"met acc avg: {sum(self.acc_met)/len(self.acc_met)}\n"

        content += "\n"
        content += f"muse acc@5: {len(self.acc5_muse)}\n"
        content += f"muse acc@5 perc: {len(self.acc5_muse)/len(self.bugs_list)}\n"
        content += f"muse acc@10: {len(self.acc10_muse)}\n"
        content += f"muse acc@10 perc: {len(self.acc10_muse)/len(self.bugs_list)}\n"
        content += f"muse acc avg: {sum(self.acc_muse)/len(self.acc_muse)}\n"

        print(content)

        acc_filename = self.output_csv.name.split("/")[-1].split(".")[0] + ".txt"
        acc_file = self.output_csv.parent / acc_filename
        with open(acc_file, "w") as f:
            f.write(content)

    def write_rank_results(self):
        with open(self.output_csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=self.bugs_list[0].keys())
            writer.writeheader()
            for bug in self.bugs_list:
                writer.writerow(bug)

    # +++++++++++++++++++++++
    # ++++++ Rank SBFL ++++++
    # +++++++++++++++++++++++
    def rank_sbfl_features(self, noCCTs=False):
        sbfl_features_filename = "sbfl_features.csv"
        if noCCTs:
            sbfl_features_filename = "sbfl_features_noCCTs.csv"
        
        print(f"rank on {sbfl_features_filename}")

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
            },
            "acc": {
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

            lines_executed_by_failing_tcs = get_lines_executed_by_failing_tcs_from_data(individual.dir_path)
            funcs_executed_by_failing_tcs = get_file_func_pair_executed_by_failing_tcs(lines_executed_by_failing_tcs)
            number_of_funcs_executed_by_failing_tcs = len(funcs_executed_by_failing_tcs)
            print(f"\tnumber of func. executed by failing tcs: {number_of_funcs_executed_by_failing_tcs}")


            cnt += 1

            ranks = {}
            for sbfl_formula in sbfl_formulas:
                rank_data = get_sbfl_rank_at_method_level(
                    individual.dir_path / sbfl_features_filename,
                    buggy_line_key, sbfl_formula,
                    funcs_executed_by_failing_tcs
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
                    if key == "acc":
                        director = f"rank of buggy function among functions executed by failing tcs ({formula})"
                        rank = ranks[formula][director]
                        acc = (rank / number_of_funcs_executed_by_failing_tcs) * 100
                        self.accuracy[key][formula].append(acc)
                    else:
                        thresh = 5 if key == "acc@5" else 10
                        if ranks[formula][bug_rank_key] <= thresh:
                            self.accuracy[key][formula].append(individual.name)              
        
        self.print_sbfl_accuracy()
        self.write_sbfl_rank_results()
    
    def print_sbfl_accuracy(self):
        content = "\n\n"
        for key, value in self.accuracy.items():
            for formula, bugs in value.items():
                if key == "acc":
                    print(bugs)
                    content += f"{key} {formula}: {sum(bugs)/len(bugs)}\n"
                else:
                    content += f"{key} {formula}: {len(bugs)}\n"
                    content += f"{key} {formula} perc: {len(bugs)/len(self.bugs_list)}\n"
        
        print(content)
        
        acc_filename = self.output_csv.name.split("/")[-1].split(".")[0] + ".txt"
        acc_file = self.output_csv.parent / acc_filename
        with open(acc_file, "w") as f:
            f.write(content)

    def write_sbfl_rank_results(self):
        with open(self.output_csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=self.bugs_list[0].keys())
            writer.writeheader()
            for bug in self.bugs_list:
                writer.writerow(bug)
