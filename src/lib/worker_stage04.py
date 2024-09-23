import subprocess as sp
import random
import csv
import time
import shutil
import filecmp
import multiprocessing

from lib.utils import *
from lib.worker_base import Worker
from lib.susp_score_formula import *

class WorkerStage04(Worker):
    def __init__(
            self, subject_name, machine, core, version_name, trial,
            verbose=False, past_trials=None, exclude_init_lines=False, # 2024-08-13 exclude lines executed on initialization
            parallel_cnt=0, parallel_mode=False# 2024-08-13 implement parallel mode
        ):
        self.trial = trial
        self.past_trials = past_trials
        self.stage_name = f"stage04-{trial}" # 2024-08-07 add-mbfl
        self.exclude_init_lines = exclude_init_lines
        self.parallel_cnt = parallel_cnt
        self.parallel_mode = parallel_mode
        super().__init__(subject_name, self.stage_name, "extracting_mbfl_features", machine, core, verbose)
        
        self.assigned_works_dir = self.core_dir / f"{self.stage_name}-assigned_works" # 2024-08-07 add-mbfl
        self.version_name = version_name

        self.version_dir = self.assigned_works_dir / version_name

        # Work Information >>
        self.target_code_file, self.buggy_code_filename, self.buggy_lineno = self.get_bug_info(self.version_dir)
        self.target_code_file_path = self.core_dir / self.target_code_file
        assert version_name == self.buggy_code_filename, f"Version name {version_name} does not match with buggy code filename {self.buggy_code_filename}"
    
        self.set_testcases(self.version_dir)
        self.set_lines_executed_by_failing_tc(self.version_dir, self.target_code_file_path, self.buggy_lineno)
        self.set_line2function_dict(self.version_dir)
        self.set_filtered_files_for_gcovr()
        self.set_target_preprocessed_files()

        self.buggy_code_file = self.get_buggy_code_file(self.version_dir, self.buggy_code_filename)
        self.buggy_line_key = self.make_key(self.target_code_file, self.buggy_lineno)

        self.musicup_exe = self.tools_dir / "music"

        self.core_repo_dir = self.core_dir / self.name

        self.mbfl_features_dir = out_dir / f"{self.name}" / "mbfl_features"
        self.mbfl_features_dir.mkdir(exist_ok=True, parents=True)

        self.mbfl_generated_mutants_dir = out_dir / f"{self.name}" / f"generated_mutants-mbfl-{self.trial}"
        self.mbfl_generated_mutants_dir.mkdir(exist_ok=True, parents=True)

        self.version_mutant_zip = self.mbfl_generated_mutants_dir / f"{self.version_name}.zip"
        self.version_mutant_dir = self.mbfl_generated_mutants_dir / self.version_name

        self.postprocessed_cov_file = self.version_dir / "coverage_info" / "postprocessed_coverage.csv"
        assert self.postprocessed_cov_file.exists(), f"Postprocessed coverage file {self.postprocessed_cov_file} does not exist"

        self.postprocessed_cov_file_noCCTs = self.version_dir / "coverage_info" / "postprocessed_coverage_noCCTs.csv"
        assert self.postprocessed_cov_file_noCCTs.exists(), f"Postprocessed coverage file {self.postprocessed_cov_file_noCCTs} does not exist"

        self.mutant2tcs_results_dir = self.version_dir / f"mutant2tcs_results-{self.trial}"
        self.mutant2tcs_results_dir.mkdir(exist_ok=True, parents=True)

        self.selected_mutant_filename = f"selected_mutants-{self.trial}.csv"
        self.mutation_testing_results_filename = f"mutation_testing_results-{self.trial}.csv"
        self.mbfl_features_filename = f"mbfl_features-{self.trial}.csv" # 2024-08-07 add-mbfl
        self.mutation_testing_results_noCCTs_filename = f"mutation_testing_results_noCCTs-{self.trial}.csv" # 2024-09-17
        self.mbfl_features_noCCTs_filename = f"mbfl_features_noCCTs-{self.trial}.csv" # 2024-09-17

    def run(self):
        print(f"Testing version {self.version_dir.name} on {self.machine}::{self.core}")

        self.selected_mutants_file = self.version_dir / self.selected_mutant_filename
        # if number_of_lines_to_mutation_test is -1, then it means we are not going to reduce target lines
        if self.number_of_lines_to_mutation_test > 0 and not self.selected_mutants_file.exists() and self.past_trials == None:
            self.lines_executed_by_failing_tcs = self.reduced_lines_executed_by_failing_tcs()
        # self.print_lines_executed_by_failing_tcs()
        elif self.past_trials != None: # 2024-08-07 add-mbfl
            self.past_selected_mutants = self.get_past_selected_mutants()
            # print(json.dumps(self.past_selected_mutants, indent=2))
            self.print_lines_executed_by_failing_tcs()
            self.lines_executed_by_failing_tcs = self.reduced_lines_executed_by_failing_tcs_based_on_past_trial()
            self.print_lines_executed_by_failing_tcs()

        # 1. Generate mutants
        if not self.version_mutant_zip.exists() and not self.version_mutant_dir.exists():
            res = self.generate_mutants_start()
            if res != 0:
                print(f"Failed to generate mutants on {self.version_dir.name}")
                return
        elif self.version_mutant_zip.exists() and not self.version_mutant_dir.exists():
            self.unzip_mutants(self.version_mutant_zip, self.mbfl_generated_mutants_dir, self.version_mutant_dir)
        elif not self.version_mutant_zip.exists() and self.version_mutant_dir.exists():
            print(f"Mutants are already generated on {self.version_dir.name}")
        self.targetfile_and_mutantdir = self.initialize_mutants_dir()

        # unzip past mutation files
        if self.past_trials != None: # 2024-08-07 add-mbfl
            for past_trial_name in self.past_trials:
                past_mbfl_generated_mutants_dir = out_dir / f"{self.name}" / f"generated_mutants-mbfl-{past_trial_name}"
                assert past_mbfl_generated_mutants_dir.exists(), f"{past_mbfl_generated_mutants_dir} doesn't exists"

                past_version_mutant_zip = past_mbfl_generated_mutants_dir / f"{self.version_name}.zip"
                past_version_mutant_dir = past_mbfl_generated_mutants_dir / self.version_name
                if past_version_mutant_zip.exists() and not past_version_mutant_dir.exists():
                    self.unzip_mutants(past_version_mutant_zip, past_mbfl_generated_mutants_dir, past_version_mutant_dir)
                elif not past_version_mutant_zip.exists() and past_version_mutant_dir.exists():
                    print(f"Mutants are already generated on {past_version_mutant_dir.name}")
        
        # 2. Reset subject repo
        self.clean_build()
        self.configure_no_cov()
        self.build()
        self.set_env()

        self.print_generated_mutants_stats()

        # 2. Select mutants
        # format of selected_fileline2mutants: {filename: {lineno: [[TC1.sh, TC2.sh, ...], [mutant_line_info1, mutant_line_info2, ...]]}}
        if not self.selected_mutants_file.exists() and self.past_trials == None: # 2024-08-07 add-mbfl
            self.selected_fileline2mutants = self.select_mutants()
            self.print_selected_mutants_stats()

            # !!!!!!!==============> THIS PART IS REMOVED BECUASE WE REDUCED LINES AT THE BEGINNING
            # if self.number_of_lines_to_mutation_test > 0:
            #     self.selected_fileline2mutants = self.reduced_selected_mutants()
            #     self.print_selected_mutants_stats()
            
            # 3. Save selected mutants information
            self.save_selected_mutants_info()
        elif not self.selected_mutants_file.exists() and self.past_trials != None: # 2024-08-07 add-mbfl
            self.selected_fileline2mutants = self.select_mutants_comparing_to_past_trials()
            self.print_selected_mutants_stats()

            # !!!!!!!==============> THIS PART IS REMOVED BECUASE WE REDUCED LINES AT THE BEGINNING
            # if self.number_of_lines_to_mutation_test > 0:
            #     self.selected_fileline2mutants = self.reduced_selected_mutants()
            #     self.print_selected_mutants_stats()
            
            # 3. Save selected mutants information
            self.save_selected_mutants_info()

        # 4. Get selected mutants
        self.selected_mutants = self.get_selected_mutants()
        self.print_selected_mutants_info()

        # 4. Conduct mutation testing
        if self.parallel_cnt == 0: # 2024-08-13 implement parallel mode
            self.begin_mbfl_process()
        else:
            self.begin_mbfl_parallel_process()

        if self.parallel_mode == False:
            # 5. Measure MBFL features
            self.mbfl_features, self.mbfl_features_noCCTs = self.measure_mbfl_features()

            # 6. process to csv
            self.process2csv(self.mbfl_features, self.mbfl_features_filename, "mbfl_features.csv")
            self.process2csv(self.mbfl_features_noCCTs, self.mbfl_features_noCCTs_filename, "mbfl_features_noCCTs.csv")

            # # 8. Zip mutant dir
            self.zip_mutants(self.version_mutant_zip, self.mbfl_generated_mutants_dir, self.version_mutant_dir)
            # unzip past mutation files
            if self.past_trials != None: # 2024-08-07 add-mbfl
                for past_trial_name in self.past_trials:
                    past_mbfl_generated_mutants_dir = out_dir / f"{self.name}" / f"generated_mutants-mbfl-{past_trial_name}"
                    assert past_mbfl_generated_mutants_dir.exists(), f"{past_mbfl_generated_mutants_dir} doesn't exists"

                    past_version_mutant_zip = past_mbfl_generated_mutants_dir / f"{self.version_name}.zip"
                    past_version_mutant_dir = past_mbfl_generated_mutants_dir / self.version_name
                    self.zip_mutants(past_version_mutant_zip, past_mbfl_generated_mutants_dir, past_version_mutant_dir)

            # 7. Save version
            self.save_version(self.version_dir, self.mbfl_features_dir)

    def reduced_lines_executed_by_failing_tcs_based_on_past_trial(self): # 2024-08-07 add-mbfl
        reduced_dict = {}
        for filename, fileline2tcs in self.lines_executed_by_failing_tcs.items():
            filename_last = filename.split("/")[-1]

            # file is in past selected file
            if filename_last in self.past_selected_mutants.keys():
                if filename not in reduced_dict:
                    reduced_dict[filename] = {}
                
                for line, tcs in fileline2tcs.items():
                    # lineno is in past selected line
                    if line in self.past_selected_mutants[filename_last].keys():
                        if line not in reduced_dict[filename]:
                            reduced_dict[filename][line] = tcs
        for filename in self.lines_executed_by_failing_tcs.keys():
            if filename not in reduced_dict:
                reduced_dict[filename] = {}
        return reduced_dict
    
    def reduced_lines_executed_by_failing_tcs(self):
        buggy_code_filename = self.target_code_file_path.name
        reduced_dict = {}
        total_selected_lines = 0

        init_filenm2lineno = {}
        if self.exclude_init_lines == True: # 2024-08-13 exclude lines executed on initialization
            init_filenm2lineno = get_linse_exected_on_initialization_as_filenm2lineno(self.version_dir)

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
                if filename == buggy_code_filename and line == self.buggy_lineno:
                    continue
                list_of_lines.append((filename, line, tcs))

        random.shuffle(list_of_lines)
        print(f">>> candidate lines: {len(list_of_lines)}")

        idx = 0
        for filename, line, tcs in list_of_lines:
            idx += 1
            if total_selected_lines >= self.number_of_lines_to_mutation_test:
                break
            if self.exclude_init_lines == False: # 2024-08-13 exclude lines executed on initialization
                if filename not in reduced_dict:
                    reduced_dict[filename] = {}
                reduced_dict[filename][line] = tcs
                total_selected_lines += 1
            else:
                if filename in init_filenm2lineno:
                    if line in init_filenm2lineno[filename]:
                        print(f">>>[{idx}] candidate not-included: {filename}:{line}")
                        continue
                if filename not in reduced_dict:
                    reduced_dict[filename] = {}
                print(f">>> [{idx}]candidate included: {filename}:{line}")
                reduced_dict[filename][line] = tcs
                total_selected_lines += 1
        
        if total_selected_lines == self.number_of_lines_to_mutation_test: # 2024-08-13 exclude lines executed on initialization
            print(f">>> Selected maximum available lines {total_selected_lines}/{self.number_of_lines_to_mutation_test}")
        else:
            print(f">>> Selected below maximum available lines {total_selected_lines}/{self.number_of_lines_to_mutation_test}")
        
        # add empty dict for files that are not selected
        for filename in self.lines_executed_by_failing_tcs.keys():
            if filename not in reduced_dict:
                reduced_dict[filename] = {}
        
        return reduced_dict
        
    
    def zip_mutants(self, version_mutant_zip, mbfl_generated_mutants_dir, version_mutant_dir):
        if version_mutant_zip.exists():
            # remove the mutant dir
            sp.check_call(["rm", "-rf", version_mutant_dir], stdout=sp.PIPE, stderr=sp.PIPE)
            print(f">> Removed mutants on {self.version_dir.name}")
        else:
            # zip the mutant dir
            cmd = ["zip", "-r", "-q", version_mutant_zip.name, version_mutant_dir.name]
            print_command(cmd, self.verbose)
            sp.check_call(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=mbfl_generated_mutants_dir)
            print(f">> Zipped mutants on {self.version_dir.name}")

            sp.check_call(["rm", "-rf", version_mutant_dir], stdout=sp.PIPE, stderr=sp.PIPE)
            print(f">> Removed mutants on {self.version_dir.name}")
    
    def get_selected_mutants(self):
        self.selected_mutants_file = self.version_dir / self.selected_mutant_filename
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
    
    def get_past_selected_mutants(self): # 2024-08-07 add-mbfl
        cnt = 0
        selected_mutants = {}
        for past_trial_name in self.past_trials:
            past_selected_mutants_file = self.version_dir / f"selected_mutants-{past_trial_name}.csv"
            assert past_selected_mutants_file.exists(), f"{past_selected_mutants_file} doesn't exist"

            with open(past_selected_mutants_file, "r") as f:
                lines = f.readlines()
                mutants = lines[2:]
                for mutant_line in mutants:
                    mutant_line = mutant_line.strip()
                    info = mutant_line.split(",")

                    target_filename = info[0]
                    mutant_id = info[1]
                    lineno = info[2]
                    failing_tcs_at_line = info[3]
                    mutant_name = info[4]

                    if target_filename not in selected_mutants:
                        selected_mutants[target_filename] = {}
                    
                    if lineno not in selected_mutants[target_filename]:
                        cnt += 1
                        selected_mutants[target_filename][lineno] = []
                    
                    selected_mutants[target_filename][lineno].append({
                        'mutant_id': mutant_id,
                        '#_failing_tcs_@line': failing_tcs_at_line,
                        'mutant_name': mutant_name,
                        "trial_name": past_trial_name
                    })
        print(f"total line from past {cnt}")
        return selected_mutants



    def measure_mbfl_features(self):
        self.total_num_of_failing_tcs = len(self.failing_tcs_list)
        self.lines_from_pp_cov = self.get_lines_from_pp_cov(self.postprocessed_cov_file)
        perfileline_features, total_p2f, total_f2p = self.get_perfileline_features(self.mutation_testing_results_filename)

        self.lines_from_pp_cov = self.get_lines_from_pp_cov(self.postprocessed_cov_file_noCCTs) # 2024-09-17
        perfileline_features_noCCTs, total_p2f_noCCTs, total_f2p_noCCTs = self.get_perfileline_features(self.mutation_testing_results_noCCTs_filename) # 2024-09-17

        # start measurement
        mbfl_features = self.measure_mbfl_scores(perfileline_features, total_p2f, total_f2p)
        mbfl_features_noCCTs = self.measure_mbfl_scores(perfileline_features_noCCTs, total_p2f_noCCTs, total_f2p_noCCTs) # 2024-09-17
        return mbfl_features, mbfl_features_noCCTs
    
    def process2csv(self, mbfl_features, filename, final_filename):
        csv_file = self.version_dir / filename

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
        
        final_file = csv_file.parent / final_filename
        shutil.copy(csv_file, final_file) # 2024-08-07 add-mbfl
    
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
    
    def get_perfileline_features(self, filename_type):
        mutation_testing_results = self.version_dir / filename_type
        assert mutation_testing_results.exists(), f"Mutation testing result file {mutation_testing_results} does not exist"

        perfileline_features = {}
        total_p2f = 0
        total_f2p = 0

        with open(mutation_testing_results, 'r') as f:
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
            "passing": self.passing_tcs_list + self.ccts_list
        }
        for type, tcs in self.utilized_testcases.items():
            print(f">> # of {type} test cases: {len(tcs)}")
        
        # 1. Initiate version results csv file
        self.mutation_testing_results = self.version_dir / self.mutation_testing_results_filename
        self.mutation_testing_results_fp = self.mutation_testing_results.open("w")
        self.mutation_testing_results_fp.write("target_file,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,build_result,p2f,p2p,f2p,f2f,p2f_tcs,p2p_tcs,f2p_tcs,f2f_tcs\n")

        self.mutation_testing_results_noCCTs = self.version_dir / self.mutation_testing_results_noCCTs_filename
        self.mutation_testing_results_noCCTs_fp = self.mutation_testing_results_noCCTs.open("w")
        self.mutation_testing_results_noCCTs_fp.write("target_file,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,build_result,p2f,p2p,f2p,f2f,p2f_tcs,p2p_tcs,f2p_tcs,f2f_tcs\n")

        # 2. Apply version patch
        patch_file = self.make_patch_file(self.target_code_file_path, self.buggy_code_file, "version.patch")
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, False)

        # 3. Conduct mutation testing
        self.conduct_mutation_testing()

        # 4. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)

        # 5. Close result csv file
        self.mutation_testing_results_fp.close()
        self.mutation_testing_results_noCCTs_fp.close()
    
    def begin_mbfl_parallel_process(self): # 2024-08-13 implement parallel mode
        # 1. copy current core<n> directory as core<n>-p<n>
        for idx in range(self.parallel_cnt):
            parall_core_name = f"{self.core_dir.name}-p{idx}"
            parall_core_dir = self.core_dir.parent / parall_core_name
            if parall_core_dir.exists():
                shutil.rmtree(parall_core_dir)
            # core_dir
            parall_core_dir.mkdir(exist_ok=True, parents=True)
            # assigned_works dir
            parall_assigned_works_dir = parall_core_dir / f"{self.stage_name}-assigned_works"
            parall_assigned_works_dir.mkdir(exist_ok=True, parents=True)
            # version_dir
            parall_version_dir = parall_assigned_works_dir / self.version_name
            shutil.copytree(self.version_dir, parall_version_dir)
            # subject-repo
            parall_repo_dir = parall_core_dir / self.name
            core_repo_dir = self.core_dir / self.name
            shutil.copytree(core_repo_dir, parall_repo_dir)

        # 2. divide the selected mutants
        selected_mutants_file = self.version_dir / self.selected_mutant_filename
        selected_mutants_csv_row = get_list_of_selected_mutants_csv_row(selected_mutants_file)
        parted_selected_mutants_csv_row = divide_list(selected_mutants_csv_row, self.parallel_cnt)
        assert len(parted_selected_mutants_csv_row) == self.parallel_cnt, f"the length of parted doesn't equal parallel_cnt {self.parallel_cnt}"
        
        # 3. alter core<n>-p<n>/stage04-trial1-assigned_works/<version-name>/selected_mutants-<trial-cnt>.csv
        for idx in range(self.parallel_cnt):
            parall_core_name = f"{self.core_dir.name}-p{idx}"
            parall_core_dir = self.core_dir.parent / parall_core_name
            assert parall_core_dir.exists(), f"{parall_core_dir.name} doesn't exist!"

            parall_assigned_works_dir = parall_core_dir / f"{self.stage_name}-assigned_works"
            assert parall_assigned_works_dir.exists(), f"{parall_assigned_works_dir.name} doesn't exist!"
            
            parall_version_dir = parall_assigned_works_dir / self.version_name
            assert parall_version_dir.exists(), f"{parall_version_dir.name} doesn't exist!"

            parall_selected_mutant_file = parall_version_dir / self.selected_mutant_filename
            assert parall_selected_mutant_file.exists(), f"{parall_selected_mutant_file.name} doesn't exist!"

            parall_selected_mutants_csv_row = parted_selected_mutants_csv_row[idx]

            self.update_parall_selected_mutants_csv(parall_selected_mutant_file, parall_selected_mutants_csv_row)

        # 4. execute mbfl extraction on core<n>-p<n>
        jobs = []
        job_args = {}
        for idx in range(self.parallel_cnt):
            machine_name = self.machine
            core_name = f"{self.core_dir.name}-p{idx}"
            version_name = self.version_name
            job = multiprocessing.Process(
                target=self.test_single_core_parall,
                args=(machine_name, core_name, version_name)
            )
            job_args[job.name] = [machine_name, core_name, version_name]
            jobs.append(job)
            job.start()

        finished_jobs = []
        for job in jobs:
            job.join()
            print(f"Job {job.name} has been finished: {job_args[job.name]}")
            finished_jobs.append(job)
            # jobs.remove(job)

        # 5. combine core<n>-p<n>/stage04-trial1-assigned_works/<version-name>/mutation_testing_results-<trial-cnt>.csv from all core<n>-p<n>
        total_mutation_testing_results_csv_row = []
        total_mutation_testing_results_noCCTs_csv_row = []
        for idx in range(self.parallel_cnt):
            parall_core_name = f"{self.core_dir.name}-p{idx}"
            parall_core_dir = self.core_dir.parent / parall_core_name
            assert parall_core_dir.exists(), f"{parall_core_dir.name} doesn't exist!"

            parall_assigned_works_dir = parall_core_dir / f"{self.stage_name}-assigned_works"
            assert parall_assigned_works_dir.exists(), f"{parall_assigned_works_dir.name} doesn't exist!"
            
            parall_version_dir = parall_assigned_works_dir / self.version_name
            assert parall_version_dir.exists(), f"{parall_version_dir.name} doesn't exist!"

            parall_mutation_testing_results_csv = parall_version_dir / self.mutation_testing_results_filename
            assert parall_mutation_testing_results_csv.exists(), f"{parall_mutation_testing_results_csv.name} doesn't exist!"
            
            mutation_testing_results_csv_row = get_mutation_testing_results_csv_row(parall_mutation_testing_results_csv)
            total_mutation_testing_results_csv_row.extend(mutation_testing_results_csv_row)

            parall_mutation_testing_results_noCCTs_csv = parall_version_dir / self.mutation_testing_results_noCCTs_filename
            assert parall_mutation_testing_results_noCCTs_csv.exists(), f"{parall_mutation_testing_results_noCCTs_csv.name} doesn't exist!"

            mutation_testing_results_noCCTs_csv_row = get_mutation_testing_results_csv_row(parall_mutation_testing_results_noCCTs_csv)
            total_mutation_testing_results_noCCTs_csv_row.extend(mutation_testing_results_noCCTs_csv_row)
            
        dest_mutation_testing_results_csv = self.version_dir / self.mutation_testing_results_filename
        self.fill_mutation_testing_results_as_final(dest_mutation_testing_results_csv, total_mutation_testing_results_csv_row)

        dest_mutation_testing_results_noCCTs_csv = self.version_dir / self.mutation_testing_results_noCCTs_filename
        self.fill_mutation_testing_results_as_final(dest_mutation_testing_results_noCCTs_csv, total_mutation_testing_results_noCCTs_csv_row)

        # 6. copy files in  mutant2tcs_results-<trial-cnt> directory
        total_mutant2tc_result_files = []
        for idx in range(self.parallel_cnt):
            parall_core_name = f"{self.core_dir.name}-p{idx}"
            parall_core_dir = self.core_dir.parent / parall_core_name
            assert parall_core_dir.exists(), f"{parall_core_dir.name} doesn't exist!"

            parall_assigned_works_dir = parall_core_dir / f"{self.stage_name}-assigned_works"
            assert parall_assigned_works_dir.exists(), f"{parall_assigned_works_dir.name} doesn't exist!"
            
            parall_version_dir = parall_assigned_works_dir / self.version_name
            assert parall_version_dir.exists(), f"{parall_version_dir.name} doesn't exist!"

            parall_mutant2tcs_results_dir = parall_version_dir / self.mutant2tcs_results_dir.name
            assert parall_mutant2tcs_results_dir.exists(), f"{parall_mutant2tcs_results_dir.name} doesn't exist!"

            for mut2tc_file in parall_mutant2tcs_results_dir.iterdir():
                print_command(["cp", "-r", mut2tc_file, self.mutant2tcs_results_dir], self.verbose)
                sp.check_call(["cp", mut2tc_file, self.mutant2tcs_results_dir])
        # 7. delete core<n>-p<n> and exits
        for idx in range(self.parallel_cnt):
            parall_core_name = f"{self.core_dir.name}-p{idx}"
            parall_core_dir = self.core_dir.parent / parall_core_name
            if parall_core_dir.exists():
                shutil.rmtree(parall_core_dir)
    
    def test_single_core_parall(self, machine, core, version):
        print(f"Testing on {machine}::{core}")
        subject_name = self.name
        machine_name = machine
        core_name = core
        need_configure = True
        version_name = self.version_name

        cmd = [
            "python3", "test_version_mbfl_features.py",
            "--subject", subject_name, "--machine", machine_name, "--core", core_name,
            "--trial", self.trial,
            "--version", version_name
        ]

        if self.verbose:
            cmd.append("--verbose")
        if self.past_trials != None:
            cmd.append("--past-trials")
            cmd.extend(self.past_trials)
        cmd.append("--parallel-mode")
        
        print_command(cmd, self.verbose)
        res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=src_dir)

        # write stdout and stderr to self.log
        log_file = self.log / f"{machine_name}-{core_name}.log"
        with log_file.open("a") as f:
            f.write(f"\n+++++ results for {version_name} +++++\n")
            f.write("+++++ STDOUT +++++\n")
            f.write(res.stdout.decode())
            f.write("\n+++++ STDERR +++++\n")
            f.write(res.stderr.decode())
    
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
        tc_outcome_noCCTs = {'p2f': -1, 'p2p': -1, 'f2p': -1, 'f2f': -1} # 2024-09-18 to make mbfl results without CCTs at the same time
        tc_outcome_detailed_noCCTs = {'p2f': [], 'p2p': [], 'f2p': [], 'f2f': []}
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
            self.write_result(self.mutation_testing_results_fp, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed)
            self.write_result(self.mutation_testing_results_noCCTs_fp, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs)
            return
        
        build_result = True
        tc_outcome = {'p2f': 0, 'p2p': 0, 'f2p': 0, 'f2f': 0}
        tc_outcome_noCCTs = {'p2f': 0, 'p2p': 0, 'f2p': 0, 'f2f': 0} # 2024-09-18 to make mbfl results without CCTs at the same time

        mutant2tcs_results_file = self.mutant2tcs_results_dir / f"{mutant_id}.csv"  # 2024-08-05 time for each test on each mutant
        mutant2tcs_results_fp = open(mutant2tcs_results_file, "w")
        mutant2tcs_results_fp.write("tc_name,outcome,return_code,return_code_str,time_taken\n")
        # 4. Run test cases
        for type, tcs in self.utilized_testcases.items():
            for tc_script_name in tcs:
                tc_start_time = time.time()
                outcome = ""
                
                tc_name = tc_script_name.split(".")[0]
                res = self.run_test_case(tc_script_name)
                isCCTs = False # 2024-09-18 to make mbfl results without CCTs at the same time
                if tc_script_name in self.ccts_list:
                    isCCTs = True
                if res == 0:
                    if type == "failing":
                        outcome = "f2p"
                        self.update_tc_outcome(outcome, tc_outcome, tc_outcome_detailed, tc_name)
                        if isCCTs == False:
                            self.update_tc_outcome(outcome, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs, tc_name)
                    elif type == "passing":
                        outcome = "p2p"
                        self.update_tc_outcome(outcome, tc_outcome, tc_outcome_detailed, tc_name)
                        if isCCTs == False:
                            self.update_tc_outcome(outcome, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs, tc_name)
                else:
                    if type == "failing":
                        outcome = "f2f"
                        self.update_tc_outcome(outcome, tc_outcome, tc_outcome_detailed, tc_name)
                        if isCCTs == False:
                            self.update_tc_outcome(outcome, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs, tc_name)
                    elif type == "passing":
                        outcome = "p2f"
                        self.update_tc_outcome(outcome, tc_outcome, tc_outcome_detailed, tc_name)
                        if isCCTs == False:
                            self.update_tc_outcome(outcome, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs, tc_name)
                
                tc_time_duration = time.time() - tc_start_time
                
                error_str = "code-not-found-in-listed-crash-codes"
                if res in crash_codes_dict:
                    error_str = crash_codes_dict[res]
                if res == 1:
                    error_str = "fail"
                if res == 0:
                    error_str = "pass"
                content = f"{tc_script_name},{outcome},{res},{error_str},{tc_time_duration}\n"
                mutant2tcs_results_fp.write(content)
        mutant2tcs_results_fp.close()
        
        # 5. Apply patch reverse
        self.apply_patch(target_file_path, mutant_file, patch_file, True)

        # 6. Write result to csv
        self.write_result(self.mutation_testing_results_fp, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed)
        self.write_result(self.mutation_testing_results_noCCTs_fp, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome_noCCTs, tc_outcome_detailed_noCCTs)
    
    def update_tc_outcome(self, type, outcome_num, outcome_detailed, tc_name):
        outcome_num[type] += 1
        outcome_detailed[type].append(tc_name)
    
    def write_result(self, fp, target_file_path, mutant_id, lineno, num_failing_tcs, mutant_name, build_result, tc_outcome, tc_outcome_detailed):
        build_str = "PASS" if build_result else "FAIL"
        full_tc_outcome = f"{tc_outcome['p2f']},{tc_outcome['p2p']},{tc_outcome['f2p']},{tc_outcome['f2f']}"

        p2f_tcs = "#".join(tc_outcome_detailed["p2f"])
        p2p_tcs = "#".join(tc_outcome_detailed["p2p"])
        f2p_tcs = "#".join(tc_outcome_detailed["f2p"])
        f2f_tcs = "#".join(tc_outcome_detailed["f2f"])

        fp.write(f"{target_file_path.name},{mutant_id},{lineno},{num_failing_tcs},{mutant_name},{build_str},{full_tc_outcome},{p2f_tcs},{p2p_tcs},{f2p_tcs},{f2f_tcs}\n")
        
    def get_target_file_path(self, target_file):
        for file in self.config["target_files"]:
            if file.split("/")[-1] == target_file:
                return self.core_dir / file
    
    def save_selected_mutants_info(self):
        self.selected_mutants_file = self.version_dir / self.selected_mutant_filename
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
    
    def update_parall_selected_mutants_csv(self, csv_file, mutant_rows): # 2024-08-13 implement parallel mode
        with open(csv_file, "w") as fp:
            fp.write(",,,,,,Before Mutation,,,,,After Mutation\n")
            fp.write("target filename,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,Mutation Operator,Start Line#,Start Col#,End Line#,End Col#,Target Token,Start Line#,Start Col#,End Line#,End Col#,Mutated Token,Extra Info\n")
            content = "\n".join(mutant_rows)
            fp.write(content)
    
    def fill_mutation_testing_results_as_final(self, csv_file, mutant_results_rows): # 2024-08-13 implement parallel mode
        with open(csv_file, "w") as fp:
            fp.write("target_file,mutant_id,lineno,#_failing_tcs_@line,Mutant Filename,build_result,p2f,p2p,f2p,f2f,p2f_tcs,p2p_tcs,f2p_tcs,f2f_tcs\n")
            content = "\n".join(mutant_results_rows)
            fp.write(content)
    
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
    
    def select_mutants_comparing_to_past_trials(self): # 2024-08-07 add-mbfl
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

                    mutant_file = file_mutants_dir / mutant_filename
                    assert mutant_file.exists(), f"{mutant_file} doesn't exists"
                    final_result = False
                    for mutant in self.past_selected_mutants[filename][mutant_lineno]:
                        cmp_mutant_id = mutant["mutant_id"]
                        cmp_n_failing_tcs_line = mutant["#_failing_tcs_@line"]
                        cmp_mutant_name = mutant["mutant_name"]
                        cmp_trial_name = mutant["trial_name"]

                        cmp_mbfl_generated_mutants_dir = out_dir / f"{self.name}" / f"generated_mutants-mbfl-{cmp_trial_name}"
                        assert cmp_mbfl_generated_mutants_dir.exists(), f"{cmp_mbfl_generated_mutants_dir} doesn't exists"
                        cmp_version_mutant_dir = cmp_mbfl_generated_mutants_dir / self.version_name
                        cmp_file_mutants_dir = cmp_version_mutant_dir / f"{self.name}-{filename}"
                        assert cmp_file_mutants_dir.exists(), f"File mutants directory {cmp_file_mutants_dir} does not exist"

                        cmp_mutant_file = cmp_file_mutants_dir / cmp_mutant_name
                        assert cmp_mutant_file.exists(), f"{cmp_mutant_file} doesn't exists"

                        res = filecmp.cmp(mutant_file, cmp_mutant_file)
                        print(res, mutant_file, cmp_mutant_file)
                        if res == True:
                            final_result = True
                            break
                    
                    if res == False:
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
            retcode = self.generate_mutants(compile_command, target_file, mutant_dir, lines)
            if retcode != 0:
                print(f">>> Failed to generate mutants on {filename} on mutant target {mutant_dir}")
        
        # 6. Apply patch reverse
        self.apply_patch(self.target_code_file_path, self.buggy_code_file, patch_file, True)
        
        return 0
    
    def generate_mutants(self, compile_command, target_file, mutant_dir, lines):
        print(f">> Generating mutants on {self.version_dir.name}")
        unused_ops = ",".join(not_using_operators_in_mbfl)
        executed_lines = ",".join(lines)

        ll = self.max_mutants
        n = 5
        if self.past_trials != None:
            n = self.max_mutants * (len(self.past_trials)+1)
            ll = n
        cmd = [
            self.musicup_exe,
            str(target_file),
            "-o", str(mutant_dir),
            "-ll", str(ll), # limit on line
            "-l", str(n), # limie on mutatin operator
            "-d", unused_ops,
            "-i", executed_lines,
            "-p", str(compile_command)
        ]
        print_command(cmd, self.verbose)
        # res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE) # 2024-08-13 implement parallel mode
        res = sp.run(cmd) # 2024-08-13 implement parallel mode
        return res.returncode

        

    
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
    
    def unzip_mutants(self, version_mutant_zip, mbfl_generated_mutants_dir, version_mutant_dir): # 2024-08-07 add-mbfl
        print_command(["unzip", "-q", version_mutant_zip, "-d", mbfl_generated_mutants_dir], self.verbose)
        sp.check_call(["unzip", "-q", version_mutant_zip, "-d", mbfl_generated_mutants_dir])

        print(f">> Unzipped mutants are saved at {version_mutant_dir.name}")
        assert version_mutant_dir.exists(), f"Mutant directory {version_mutant_dir} does not exist"
    
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
        total_line = 0
        selected_mutants_info = {}
        for filename, lineno_mutants in self.selected_mutants.items():
            mutant_cnt = 0
            for lineno, mutants in lineno_mutants.items():
                total_line += 1
                mutant_cnt += len(mutants)
            total_num_selected_mutants += mutant_cnt
            selected_mutants_info[filename] = mutant_cnt

        print(f">> Total number of selected mutants: {total_num_selected_mutants}")
        print(f">> Selected mutants per file (after saving selected mutants):")
        for filename, num_mutants in selected_mutants_info.items():
            print(f"\t >> {filename}: {num_mutants} mutants")
        print(f">>> total line: {total_line}")
    
    def print_lines_executed_by_failing_tcs(self):
        print(f">> Lines executed by failing test cases:")
        total_cnt = 0
        for filename, fileline2tcs in self.lines_executed_by_failing_tcs.items():
            print(f"\t >> {filename}: {len(fileline2tcs)} lines")
            total_cnt += len(fileline2tcs)
        print(f">>> total {total_cnt}")
