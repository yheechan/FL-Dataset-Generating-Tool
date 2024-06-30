import subprocess as sp
import random
import csv

from lib.utils import *
from lib.worker_base import Worker
from lib.susp_score_formula import *

class WorkerStage04(Worker):
    def __init__(
            self, subject_name, machine, core, version_name, verbose=False):
        super().__init__(subject_name, "stage04", "extracting_mbfl_features", machine, core, verbose)
        
        self.assigned_works_dir = self.core_dir / f"stage04-assigned_works"
        self.version_name = version_name

        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.target_code_file_path, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_dir)
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.version_dir)
        self.set_lines_executed_by_failing_tc(self.version_dir, self.target_code_file_path, self.buggy_lineno)
        self.set_line2function_dict(self.version_dir)
        self.set_filtered_files_for_gcovr()
        self.set_target_preprocessed_files()

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)
        self.buggy_line_key = self.make_key(self.target_code_file_path.__str__(), self.buggy_lineno)

        self.musicup_exe = self.tools_dir / "music"

        self.core_repo_dir = self.core_dir / self.name

        self.mbfl_features_dir = out_dir / f"{self.name}" / "mbfl_features"
        self.mbfl_features_dir.mkdir(exist_ok=True, parents=True)

        self.mbfl_generated_mutants_dir = out_dir / f"{self.name}" / "generated_mutants-mbfl"
        self.mbfl_generated_mutants_dir.mkdir(exist_ok=True, parents=True)

        self.version_mutant_zip = self.mbfl_generated_mutants_dir / f"{self.version_name}.zip"
        self.version_mutant_dir = self.mbfl_generated_mutants_dir / self.version_name

        self.postprocessed_cov_file = self.version_dir / "coverage_info" / "postprocessed_coverage.csv"
        assert self.postprocessed_cov_file.exists(), f"Postprocessed coverage file {self.postprocessed_cov_file} does not exist"

    def run(self):
        print(f"Testing version {self.version_dir.name} on {self.machine}::{self.core}")

        if self.number_of_lines_to_mutation_test > 0:
            self.lines_executed_by_failing_tcs = self.reduced_lines_executed_by_failing_tcs()
        # self.print_lines_executed_by_failing_tcs()

        # 1. Generate mutants
        if not self.version_mutant_zip.exists() and not self.version_mutant_dir.exists():
            res = self.generate_mutants_start()
            if res != 0:
                print(f"Failed to generate mutants on {self.version_dir.name}")
                return
        elif self.version_mutant_zip.exists() and not self.version_mutant_dir.exists():
            self.unzip_mutants()
        elif not self.version_mutant_zip.exists() and self.version_mutant_dir.exists():
            print(f"Mutants are already generated on {self.version_dir.name}")
        self.targetfile_and_mutantdir = self.initialize_mutants_dir()
        
        # 2. Reset subject repo
        self.clean_build()
        self.configure_no_cov()
        self.build()
        self.set_env()

        self.print_generated_mutants_stats()

        # 2. Select mutants
        # format of selected_fileline2mutants: {filename: {lineno: [[TC1.sh, TC2.sh, ...], [mutant_line_info1, mutant_line_info2, ...]]}}
        self.selected_fileline2mutants = self.select_mutants()
        self.print_selected_mutants_stats()

        # !!!!!!!==============> THIS PART IS REMOVED BECUASE WE REDUCED LINES AT THE BEGINNING
        # if self.number_of_lines_to_mutation_test > 0:
        #     self.selected_fileline2mutants = self.reduced_selected_mutants()
        #     self.print_selected_mutants_stats()
        
        # 3. Save selected mutants information
        self.save_selected_mutants_info()

        # # 4. Get selected mutants
        self.selected_mutants = self.get_selected_mutants()
        self.print_selected_mutants_info()

        # 4. Conduct mutation testing
        self.begin_mbfl_process()

        # 5. Measure MBFL features
        self.mbfl_features = self.measure_mbfl_features()

        # 6. process to csv
        self.process2csv(self.mbfl_features)

        # 8. Zip mutant dir
        self.zip_mutants()

        # 7. Save version
        self.save_version(self.version_dir, self.mbfl_features_dir)
    
    def reduced_lines_executed_by_failing_tcs(self):
        buggy_code_filename = self.target_code_file_path.name
        reduced_dict = {}
        total_selected_lines = 0

        if buggy_code_filename in self.lines_executed_by_failing_tcs:
            if self.buggy_lineno in self.lines_executed_by_failing_tcs[buggy_code_filename]:
                reduced_dict[buggy_code_filename] = {
                    self.buggy_lineno: self.lines_executed_by_failing_tcs[buggy_code_filename][self.buggy_lineno]
                }
                total_selected_lines += 1
            else:
                print(f">> Buggy line {self.buggy_lineno} does not have any mutants")

        list_of_lines = []
        for filename, fileline2tcs in self.lines_executed_by_failing_tcs.items():
            for line, tcs in fileline2tcs.items():
                if line != self.buggy_lineno:
                    list_of_lines.append((filename, line, tcs))

        random.shuffle(list_of_lines)

        for filename, line, tcs in list_of_lines:
            if total_selected_lines >= self.number_of_lines_to_mutation_test:
                break
            if filename not in reduced_dict:
                reduced_dict[filename] = {}
            reduced_dict[filename][line] = tcs
            total_selected_lines += 1
        
        # add empty dict for files that are not selected
        for filename in self.lines_executed_by_failing_tcs.keys():
            if filename not in reduced_dict:
                reduced_dict[filename] = {}
        
        return reduced_dict
        
    
    def zip_mutants(self):
        if self.version_mutant_zip.exists():
            # remove the mutant dir
            sp.check_call(["rm", "-rf", self.version_mutant_dir], stdout=sp.PIPE, stderr=sp.PIPE)
            print(f">> Removed mutants on {self.version_dir.name}")
        else:
            # zip the mutant dir
            cmd = ["zip", "-r", "-q", self.version_mutant_zip.name, self.version_mutant_dir.name]
            print_command(cmd, self.verbose)
            sp.check_call(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=self.mbfl_generated_mutants_dir)
            print(f">> Zipped mutants on {self.version_dir.name}")

            sp.check_call(["rm", "-rf", self.version_mutant_dir], stdout=sp.PIPE, stderr=sp.PIPE)
            print(f">> Removed mutants on {self.version_dir.name}")
    
    def get_selected_mutants(self):
        self.selected_mutants_file = self.version_dir / "selected_mutants.csv"
        assert self.selected_mutants_file.exists(), f"Selected mutants file {self.selected_mutants_file} does not exist"

        selected_mutants = {}
        with open(self.selected_mutants_file, "r") as f:
            lines = f.readlines()
            mutants = lines[2:]

            for mutant_line in mutants:
                mutant_line = mutant_line.strip()
                info = mutant_line.split(',')

                target_filename = info[0]
                mutant_id = info[1]
                lineno = info[2]
                failing_tcs_at_line = info[3]
                mutant_name = info[4]

                if target_filename not in selected_mutants:
                    selected_mutants[target_filename] = {}
                
                if lineno not in selected_mutants[target_filename]:
                    selected_mutants[target_filename][lineno] = []
                
                selected_mutants[target_filename][lineno].append({
                    'mutant_id': mutant_id,
                    '#_failing_tcs_@line': failing_tcs_at_line,
                    'mutant_name': mutant_name
                })

        return selected_mutants


    def measure_mbfl_features(self):
        self.total_num_of_failing_tcs = len(self.failing_tcs_list)
        self.lines_from_pp_cov = self.get_lines_from_pp_cov(self.postprocessed_cov_file)
        perfileline_features, total_p2f, total_f2p = self.get_perfileline_features()

        # start measurement
        mbfl_features = self.measure_mbfl_scores(perfileline_features, total_p2f, total_f2p)
        return mbfl_features
    
    def process2csv(self, mbfl_features):
        csv_file = self.version_dir / 'mbfl_features.csv'

        mutant_key_default = {}
        for i in range(1, self.max_mutants+1):
            mutant_key_default[f'm{i}:f2p'] = -1
            mutant_key_default[f'm{i}:p2f'] = -1
        
        default = {
            '# of totfailed_TCs': self.total_num_of_failing_tcs,
            '#_failing_tcs_@line': 0,
            '# of mutants': self.max_mutants,
            '|muse(s)|': 0, 'total_f2p': 0, 'total_p2f': 0,
            'line_total_f2p': 0, 'line_total_p2f': 0,
            'muse_1': 0, 'muse_2': 0, 'muse_3': 0, 'muse_4': 0,
            'muse susp. score': 0.0, 'met susp. score': 0.0, 'bug': 0,
            **mutant_key_default
        }

        fieldnames = ['key', '# of totfailed_TCs', '#_failing_tcs_@line', '# of mutants'] + list(mutant_key_default.keys()) + [
            '|muse(s)|', 'total_f2p', 'total_p2f', 'line_total_f2p', 'line_total_p2f',
            'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse susp. score', 'met susp. score',
            'bug'
        ]

        with open(csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for line in self.lines_from_pp_cov:
                line_info = line.strip().split('#')
                target_file = line_info[0].split('/')[-1]
                lineno = line_info[-1]

                buggy_stat = 0
                if line == self.buggy_line_key:
                    buggy_stat = 1
                
                if target_file in mbfl_features and lineno in mbfl_features[target_file]:
                    mbfl_features[target_file][lineno]['bug'] = buggy_stat
                    writer.writerow({
                        'key': line, **mbfl_features[target_file][lineno]
                    })
                else:
                    default['bug'] = buggy_stat
                    writer.writerow({'key': line, **default})
    
    def measure_mbfl_scores(self, perfileline_features, total_p2f, total_f2p):
        mbfl_features = {}

        for target_file, lineno_mutants in perfileline_features.items():
            if target_file not in mbfl_features:
                mbfl_features[target_file] = {}

            for lineno, mutants in lineno_mutants.items():
                if lineno not in mbfl_features[target_file]:
                    mbfl_features[target_file][lineno] = {}
                
                mbfl_features[target_file][lineno]['# of totfailed_TCs'] = self.total_num_of_failing_tcs
                mbfl_features[target_file][lineno]['# of mutants'] = self.max_mutants
                # because all mutants at same line begine with the same # of failing tcs at line
                mbfl_features[target_file][lineno]['#_failing_tcs_@line'] = mutants[0]['#_failing_tcs_@line']
                
                mutant_cnt = 0
                mutant_key_list = []
                for mutant in mutants:
                    mutant_id = mutant['mutant_id']
                    # num_failing_tcs_at_line = mutant['#_failing_tcs_@line']
                    # mutant_name = mutant['mutant_filename']
                    p2f = mutant['p2f']
                    p2p = mutant['p2p']
                    f2p = mutant['f2p']
                    f2f = mutant['f2f']

                    # ps. perfileline_features does not contain mutants that failed to build

                    mutant_cnt += 1
                    p2f_name = f"m{mutant_cnt}:p2f"
                    f2p_name = f"m{mutant_cnt}:f2p"
                    mutant_key_list.append((p2f_name, f2p_name))

                    mbfl_features[target_file][lineno][p2f_name] = p2f
                    mbfl_features[target_file][lineno][f2p_name] = f2p
                    # if f2p > 0:
                    #     print(f"Mutant {lineno} {mutant_id} ({p2f}, {p2p}, {f2p}, {f2f})")

                for i in range(0, self.max_mutants - len(mutants)):
                    mutant_cnt += 1
                    p2f_name = f"m{mutant_cnt}:p2f"
                    f2p_name = f"m{mutant_cnt}:f2p"
                    mutant_key_list.append((p2f_name, f2p_name))

                    mbfl_features[target_file][lineno][p2f_name] = -1
                    mbfl_features[target_file][lineno][f2p_name] = -1
            
                met_score = measure_metallaxis(mbfl_features[target_file][lineno], mutant_key_list)
                mbfl_features[target_file][lineno]['met susp. score'] = met_score

                muse_data = measure_muse(mbfl_features[target_file][lineno], total_p2f, total_f2p, mutant_key_list)
                for key, value in muse_data.items():
                    mbfl_features[target_file][lineno][key] = value
        
        # print(json.dumps(mbfl_features, indent=4))
        
        return mbfl_features
    
    def get_perfileline_features(self):
        self.mutation_testing_results = self.version_dir / "mutation_testing_results.csv"
        assert self.mutation_testing_results.exists(), f"Mutation testing result file {self.mutation_testing_results} does not exist"

        perfileline_features = {}
        total_p2f = 0
        total_f2p = 0

        with open(self.mutation_testing_results, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                info = line.strip().split(',')
                target_file = info[0]
                mutant_id = info[1]
                lineno = info[2]
                num_failing_tcs_at_line = int(info[3])
                mutant_filename = info[4]
                build_result = info[5]

                if build_result == 'FAIL':
                    continue

                p2f = int(info[6])
                p2p = int(info[7])
                f2p = int(info[8])
                f2f = int(info[9])

                total_p2f += p2f
                total_f2p += f2p

                if target_file not in perfileline_features:
                    perfileline_features[target_file] = {}

                if lineno not in perfileline_features[target_file]:
                    perfileline_features[target_file][lineno] = []
                
                perfileline_features[target_file][lineno].append({
                    'mutant_id': mutant_id,
                    'mutant_filename': mutant_filename,
                    '#_failing_tcs_@line': num_failing_tcs_at_line,
                    'p2f': p2f,
                    'p2p': p2p,
                    'f2p': f2p,
                    'f2f': f2f
                })
        
        # print(json.dumps(perfileline_features, indent=4))
        
        return perfileline_features, total_p2f, total_f2p

    
    def begin_mbfl_process(self):
        self.utilized_testcases = {
            "failing": self.failing_tcs_list,
            "passing": self.passing_tcs_list
        }
        for type, tcs in self.utilized_testcases.items():
            print(f">> # of {type} test cases: {len(tcs)}")
        
        # 1. Initiate version results csv file
        self.mutation_testing_results = self.version_dir / "mutation_testing_results.csv"
        self.mutation_testing_results_fp = self.mutation_testing_results.open("w")
        self.mutation_testing_results_fp.write("target_file,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,build_result,p2f,p2p,f2p,f2f,p2f_tcs,p2p_tcs,f2p_tcs,f2f_tcs\n")

        # 2. Apply version patch
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Conduct mutation testing
        self.conduct_mutation_testing()

        # 4. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)

        # 5. Close result csv file
        self.mutation_testing_results_fp.close()
    
    def conduct_mutation_testing(self):
        for target_file, lineno_mutants in self.selected_mutants.items():
            target_file_path = self.get_target_file_path(target_file)
            assert target_file_path.exists(), f"Target file {target_file_path} does not exist"

            for lineno, mutants in lineno_mutants.items():

                for mutant in mutants:
                    mutant_id = mutant["mutant_id"]
                    mutant_name = mutant["mutant_name"]
                    num_failing_tcs = mutant["#_failing_tcs_@line"]

                    mutant_file = self.version_mutant_dir / f"{self.name}-{target_file_path.name}" / mutant_name
                    assert mutant_file.exists(), f"Mutant file {mutant_file} does not exist"

                    self.start_test_on_mutant(
                        target_file_path, lineno, num_failing_tcs, mutant_id, mutant_name, mutant_file
                    )
    
    def start_test_on_mutant(self, target_file_path, lineno, num_failing_tcs, mutant_id, mutant_name, mutant_file):
        print(f">> Testing mutant {mutant_id}:{mutant_name} on {self.version_dir.name}")
        tc_outcome = {'p2f': -1, 'p2p': -1, 'f2p': -1, 'f2f': -1}
        tc_outcome_detailed = {'p2f': [], 'p2p': [], 'f2p': [], 'f2f': []}
        build_result = False

        # 1. Make patch file
        patch_file = self.make_patch_file(target_file_path, mutant_file, "mutant.patch")

        # 2. Apply patch
        self.apply_patch(target_file_path, mutant_file, patch_file, False)

        # 3. Build subject
        res = self.build()
        if res != 0:
            print(f"Failed to build on {mutant_id}:{mutant_name} of {self.version_dir.name}")
            self.apply_patch(target_file_path, mutant_file, patch_file, True)
            self.write_result(target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed)
            return
        
        build_result = True
        tc_outcome = {'p2f': 0, 'p2p': 0, 'f2p': 0, 'f2f': 0}

        # 4. Run test cases
        for type, tcs in self.utilized_testcases.items():
            for tc_script_name in tcs:
                tc_name = tc_script_name.split(".")[0]
                res = self.run_test_case(tc_script_name)
                if res == 0:
                    if type == "failing":
                        tc_outcome["f2p"] += 1
                        tc_outcome_detailed["f2p"].append(tc_name)
                    elif type == "passing":
                        tc_outcome["p2p"] += 1
                        tc_outcome_detailed["p2p"].append(tc_name)
                else:
                    if type == "failing":
                        tc_outcome["f2f"] += 1
                        tc_outcome_detailed["f2f"].append(tc_name)
                    elif type == "passing":
                        tc_outcome["p2f"] += 1
                        tc_outcome_detailed["p2f"].append(tc_name)
        
        # 5. Apply patch reverse
        self.apply_patch(target_file_path, mutant_file, patch_file, True)

        # 6. Write result to csv
        self.write_result(target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed)
    
    def write_result(self, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed):
        build_str = "PASS" if build_result else "FAIL"
        full_tc_outcome = f"{tc_outcome['p2f']},{tc_outcome['p2p']},{tc_outcome['f2p']},{tc_outcome['f2f']}"

        p2f_tcs = "#".join(tc_outcome_detailed["p2f"])
        p2p_tcs = "#".join(tc_outcome_detailed["p2p"])
        f2p_tcs = "#".join(tc_outcome_detailed["f2p"])
        f2f_tcs = "#".join(tc_outcome_detailed["f2f"])

        self.mutation_testing_results_fp.write(f"{target_file_path.name},{mutant_id},{lineno},{num_failing_tcs},{mutant_name},{build_str},{full_tc_outcome},{p2f_tcs},{p2p_tcs},{f2p_tcs},{f2f_tcs}\n")
        
    def get_target_file_path(self, target_file):
        for file in self.config["target_files"]:
            if file.split("/")[-1] == target_file:
                return self.core_dir / file
    
    def save_selected_mutants_info(self):
        self.selected_mutants_file = self.version_dir / "selected_mutants.csv"
        mutant_idx = 1
        with open(self.selected_mutants_file, "w") as f:
            f.write(",,,,,,Before Mutation,,,,,After Mutation\n")
            f.write("target filename,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,Mutation Operator,Start Line#,Start Col#,End Line#,End Col#,Target Token,Start Line#,Start Col#,End Line#,End Col#,Mutated Token,Extra Info\n")
            
            for filename, fileline2mutants in self.selected_fileline2mutants.items():
                for lineno, tc_mutant_info in fileline2mutants.items():
                    tcs = tc_mutant_info[0]

                    for mutant_line in tc_mutant_info[1]:
                        mutant_id = f"mutant_{mutant_idx}"
                        f.write(f"{filename},{mutant_id},{lineno},{len(tcs)},{mutant_line}\n")
                        mutant_idx += 1

                        mutant_info = mutant_line.split(",")
                        mutant_filename = mutant_info[0]
    
    def reduced_selected_mutants(self):
        buggy_code_filename = self.target_code_file_path.name
        # reduce selected mutants to only 500 lineno in total across all files
        # make sure buggy_lineno from self.buggy_code_filename is included in the selected mutants
        # but beware, that buggy_lineno might have 0 mutants
        # in that case we need to select mutants from other lines
        reduce_selected_file2mutants = {}
        total_selected_lines = 0

        # add buggy_lineno to selected mutants
        if buggy_code_filename in self.selected_fileline2mutants:
            if self.buggy_lineno in self.selected_fileline2mutants[buggy_code_filename]:
                reduce_selected_file2mutants[buggy_code_filename] = {self.buggy_lineno: self.selected_fileline2mutants[buggy_code_filename][self.buggy_lineno]}
                total_selected_lines += 1
            else:
                print(f">> Buggy line {self.buggy_lineno} does not have any mutants")
        
        # randomly select lineno from random files until total_selected_lines == number_of_lines_to_mutation_test
        list_of_lines = []
        for filename, fileline2mutants in self.selected_fileline2mutants.items():
            for line, tc_mutant_info in fileline2mutants.items():
                if line != self.buggy_lineno:
                    list_of_lines.append((filename, line, tc_mutant_info))
        
        random.shuffle(list_of_lines)

        for filename, line, tc_mutant_info in list_of_lines:
            if total_selected_lines >= self.number_of_lines_to_mutation_test:
                break
            if len(tc_mutant_info[1]) > 0:
                if filename not in reduce_selected_file2mutants:
                    reduce_selected_file2mutants[filename] = {}
                reduce_selected_file2mutants[filename][line] = tc_mutant_info
                total_selected_lines += 1

        return reduce_selected_file2mutants

    def select_mutants(self):
        files2mutants = {}
        tot_mutant_cnt = 0

        for target_file, fileline2tcs in self.lines_executed_by_failing_tcs.items():
            file_tot_mutant_cnt = 0

            filename = target_file.split("/")[-1]
            # initiate dictionary for selected mutants on file-line basis
            # {filename: {lineno: [[TC1.sh, TC2.sh, ...], [mutant_line_info1, mutant_line_info2, ...]]}}
            files2mutants[filename] = {}
            for lineno, tcs in fileline2tcs.items():
                files2mutants[filename][lineno] = [tcs, []]
            
            # get mutants for each line
            file_mutants_dir = self.version_mutant_dir / f"{self.name}-{filename}"
            assert file_mutants_dir.exists(), f"File mutants directory {file_mutants_dir} does not exist"
            
            code_name = target_file.split(".")[0]
            mut_db_csv_name = f"{code_name}_mut_db.csv"
            mut_db_csv = file_mutants_dir / mut_db_csv_name
            # this is when failing tcs doesn't execute any line in the target file
            if not mut_db_csv.exists():
                print(f">> Mutants database csv {mut_db_csv.name} does not exist (no mutants)")
                continue

            # print(f">> Reading mutants from {mut_db_csv.name}")
            with mut_db_csv.open() as f:
                lines = f.readlines()
                mutants = lines[2:]
                random.shuffle(mutants)
                # print(f"Total mutants: {len(mutants)}")
                for mutant_line in mutants:
                    mutant_line = mutant_line.strip()

                    # 0 Mutant Filename
                    # 1 Mutation Operator
                    # 2 Start Line#
                    # 3 Start Col#
                    # 4 End Line#
                    # 5 End Col#
                    # 6 Target Token
                    # 7 Start Line#
                    # 8 Start Col#
                    # 9 End Line#
                    # 10 End Col#
                    # 11 Mutated Token
                    # 12 Extra Info
                    info = mutant_line.split(',')
                    mutant_filename = info[0]
                    mutant_lineno = info[2]

                    # do not select mutants for lines that are not executed by failing test cases
                    if mutant_lineno not in files2mutants[filename]:
                        print(f"Mutant line {mutant_lineno} is not executed by failing test cases")
                        continue

                    # select mutant
                    if len(files2mutants[filename][mutant_lineno][1]) < self.max_mutants:
                        files2mutants[filename][mutant_lineno][1].append(mutant_line)
                        file_tot_mutant_cnt += 1
                        tot_mutant_cnt += 1

        return files2mutants

    def generate_mutants_start(self):
        self.targetfile_and_mutantdir = self.initialize_mutants_dir()
        
        # 1. Make patch file: of target version of a subject
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")

        # 2. Apply patch
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Reset subject repo
        self.clean_build()
        res = self.configure_no_cov()
        if res != 0:
            print(f"Failed to configure on {self.version_dir.name}")
            self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
            return 1
        res = self.build()
        if res != 0:
            print(f"Failed to build on {self.version_dir.name}")
            self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
            return 1
        self.set_env()

        # 4. Get compile command
        compile_command = self.core_dir / self.config["compile_command_path"]
        assert compile_command.exists(), f"Compile command file {compile_command} does not exist"

        # 5. Generate mutants
        for target_file, mutant_dir in self.targetfile_and_mutantdir:
            filename = target_file.name
            lines = list(self.lines_executed_by_failing_tcs[filename].keys())
            if len(lines) == 0:
                print(f">> No failing test case executed lines on {filename}")
                continue
            self.generate_mutants(compile_command, target_file, mutant_dir, lines)
        
        # 6. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
        
        return 0
    
    def generate_mutants(self, compile_command, target_file, mutant_dir, lines):
        print(f">> Generating mutants on {self.version_dir.name}")
        unused_ops = ",".join(not_using_operators_in_mbfl)
        executed_lines = ",".join(lines)

        cmd = [
            self.musicup_exe,
            str(target_file),
            "-o", str(mutant_dir),
            "-ll", str(self.max_mutants),
            "-l", "5",
            "-d", unused_ops,
            "-i", executed_lines,
            "-p", str(compile_command)
        ]
        print_command(cmd, self.verbose)
        sp.check_call(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

        

    
    def initialize_mutants_dir(self):
        # list: target_file, its mutants_dir
        targetfile_and_mutantdir = []
        for target_file in self.config["target_files"]:
            target_file_path = self.core_dir / target_file
            assert target_file_path.exists(), f"Target file {target_file_path} does not exist"

            target_file_name = target_file.split("/")[-1]
            # single_file_mutant_dir = self.version_mutant_dir / target_file_name
            single_file_mutant_dir = self.version_mutant_dir / f"{self.name}-{target_file_name}"
            print_command(["mkdir", "-p", single_file_mutant_dir], self.verbose)
            single_file_mutant_dir.mkdir(exist_ok=True, parents=True)

            targetfile_and_mutantdir.append((target_file_path, single_file_mutant_dir))
        return targetfile_and_mutantdir
    
    def unzip_mutants(self):
        print_command(["unzip", "-q", self.version_mutant_zip, "-d", self.mbfl_generated_mutants_dir], self.verbose)
        sp.check_call(["unzip", "-q", self.version_mutant_zip, "-d", self.mbfl_generated_mutants_dir])

        print(f">> Unzipped mutants are saved at {self.version_mutant_dir.name}")
        assert self.version_mutant_dir.exists(), f"Mutant directory {self.version_mutant_dir} does not exist"
    
    def print_generated_mutants_stats(self):
        total_num_mutants = 0
        total_num_lines_executed = 0
        mutant_cnt_per_file = {}
        for target_file, mutant_dir in self.targetfile_and_mutantdir:
            # mutant_files is a list of files that do not end with .csv
            mutant_files = [f for f in mutant_dir.iterdir() if not f.name.endswith(".csv")]
            num_mutants = len(mutant_files)
            total_num_mutants += num_mutants
            mutant_cnt_per_file[target_file] = num_mutants

            # get number of lines executed by failing test cases
            filename = target_file.name
            if filename in self.lines_executed_by_failing_tcs:
                total_num_lines_executed += len(self.lines_executed_by_failing_tcs[filename])


        print(f">> Total number of mutants: {total_num_mutants}")
        print(f">> Total number of lines executed by failing test cases: {total_num_lines_executed}")
        print(f">> Mutants per file:")
        for target_file, num_mutants in mutant_cnt_per_file.items():
            print(f"\t >> {target_file.name}: {num_mutants} mutants, {len(self.lines_executed_by_failing_tcs[target_file.name])} lines executed by failing test cases")
    
    def print_selected_mutants_stats(self):
        total_num_selected_mutants = 0
        total_num_lines = 0
        selected_mutant_cnt_per_file = {}
        for filename, fileline2mutants in self.selected_fileline2mutants.items():
            for lineno, tc_mutant_info in fileline2mutants.items():
                total_num_lines += 1
                total_num_selected_mutants += len(tc_mutant_info[1])
                if filename not in selected_mutant_cnt_per_file:
                    selected_mutant_cnt_per_file[filename] = 0
                selected_mutant_cnt_per_file[filename] += len(tc_mutant_info[1])
        print(f">> Total number of selected mutants: {total_num_selected_mutants}")
        print(f">> Total number of lines: {total_num_lines}")
        print(f">> Selected mutants per file:")
        for filename, num_mutants in selected_mutant_cnt_per_file.items():
            print(f"\t >> {filename}: {num_mutants} mutants")

    def print_selected_mutants_info(self):
        total_num_selected_mutants = 0
        selected_mutants_info = {}
        for filename, lineno_mutants in self.selected_mutants.items():
            mutant_cnt = 0
            for lineno, mutants in lineno_mutants.items():
                mutant_cnt += len(mutants)
            total_num_selected_mutants += mutant_cnt
            selected_mutants_info[filename] = mutant_cnt

        print(f">> Total number of selected mutants: {total_num_selected_mutants}")
        print(f">> Selected mutants per file (after saving selected mutants):")
        for filename, num_mutants in selected_mutants_info.items():
            print(f"\t >> {filename}: {num_mutants} mutants")
    
    def print_lines_executed_by_failing_tcs(self):
        print(f">> Lines executed by failing test cases:")
        for filename, fileline2tcs in self.lines_executed_by_failing_tcs.items():
            print(f"\t >> {filename}: {len(fileline2tcs)} lines")