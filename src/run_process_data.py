import subprocess
import threading
import json

def run_command(command):
    """Runs a shell command and waits for it to complete."""
    subprocess.run(command, shell=True, stdout=subprocess.PIPE)

def execute_commands(subjects, command_sequences):
    """
    Executes command sequences in parallel for each subject,
    ensuring all subjects finish each step before moving to the next.
    """
    for command_template, analysis_config_json in command_sequences:
        threads = []

        # dump analysis_config_json to ../configs/analysis_config.json
        with open("../configs/analysis_config.json", "w") as f:
            json.dump(analysis_config_json, f, indent=4)
        
        for subject in subjects:
            cmd = command_template.replace("--subject subject_name_here", f"--subject {subject}")
            thread = threading.Thread(target=run_command, args=(cmd,))
            threads.append(thread)
            thread.start()
            print(f">>> Running {cmd}")
        
        for thread in threads:
            thread.join()
        
        print(f">>> Finished running {command_template}")
        print()

if __name__ == "__main__":
    subjects = [
        "zlib_ng_exp1",
        "libxml2_exp1",
        "opencv_features2d_exp1",
        "opencv_imgproc_exp1",
        "opencv_core_exp1",
        "jsoncpp_exp1",
        # "opencv_calib3d_exp1"
    ]

    command_sequences = [
        # RQ1-1 Line Selection Method
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name allfails-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "all_fails",
        #     "line_selection_rate": 100.0,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name rand50-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "rand",
        #     "line_selection_rate": 0.5,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.5,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # RQ1-2 Line Selection Amount
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.3,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.2,
            "mut_cnt_config": [10],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 10, 10],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "all",
            "tc_reduction_rate": 1.0,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-maxMutants-excludeCCT", { --> THIS WAS USED ALSO FOR RQ2
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish201-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.01,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish200-maxMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.0,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [10, 10, 10],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # RQ2 Mutation # Control
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced5Mutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.3,
            "mut_cnt_config": [5],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "reduced_num_mut",
            "mutant_num_std": [5, 5, 5],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "all",
            "tc_reduction_rate": 1.0,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced3Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.3,
        #     "mut_cnt_config": [3],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [3, 3, 3],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced1Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.3,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced5Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.2,
        #     "mut_cnt_config": [5],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [5, 5, 5],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.2,
        #     "mut_cnt_config": [3],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [3, 3, 3],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced1Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.2,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced5Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [5],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "reduced_num_mut",
        #     "mutant_num_std": [5, 5, 5],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-noMutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [0],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [0, 0, 0],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced7Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [7],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [7, 7, 7],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced3Mutants-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [3],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [3, 3, 3],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        
        # THIS IS DEPRECATED NO USE FOR RESEARCH
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reducedSbflnaish2-excludeCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [10],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "sbfl",
        #     "mutant_num_std": [10, 6, 2],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # RQ3 Include CCT
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-withCCT", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "all",
        #     "tc_reduction_rate": 1.0,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": True,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # # RQ4 Reduce TC
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov70", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "branch_cov_rate",
        #     "tc_reduction_rate": 0.7,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov50", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "branch_cov_rate",
        #     "tc_reduction_rate": 0.5,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov30", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "branch_cov_rate",
        #     "tc_reduction_rate": 0.3,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],
        # ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish210-reduced1Mutants-excludeCCT-reducedTCBranchCov10", {
        #     "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
        #     "line_selection_method": "sbfl",
        #     "line_selection_rate": 0.1,
        #     "mut_cnt_config": [1],

        #     "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
        #     "mutant_num_method": "all_fails",
        #     "mutant_num_std": [1, 1, 1],

        #     "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
        #     "tc_reduction_method": "branch_cov_rate",
        #     "tc_reduction_rate": 0.1,

        #     "sbfl_standard": "naish2_5",
        #     "experiment_repeat": 1,
        #     "include_cct": False,
        #     "apply_heuristic": False,
        #     "versions_to_remove": [],
        #     "deliberate_inclusion": False
        # }],

        # RQ4_20
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov70", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "branch_cov_rate",
            "tc_reduction_rate": 0.7,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov50", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "branch_cov_rate",
            "tc_reduction_rate": 0.5,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov30", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "branch_cov_rate",
            "tc_reduction_rate": 0.3,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedTCBranchCov10", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "branch_cov_rate",
            "tc_reduction_rate": 0.1,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],

        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom70", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "random_rate",
            "tc_reduction_rate": 0.7,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom50", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "random_rate",
            "tc_reduction_rate": 0.5,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom30", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "random_rate",
            "tc_reduction_rate": 0.3,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish220-reduced3Mutants-excludeCCT-reducedRandom10", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "mut_cnt_config": [1],

            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [1, 1, 1],

            "list_of_tc_reduction_methods": ["all", "random_rate", "random_equal", "branch_cov_rate", "branch_cov_equal"],
            "tc_reduction_method": "random_rate",
            "tc_reduction_rate": 0.1,

            "sbfl_standard": "naish2_5",
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
    ]
    
    execute_commands(subjects, command_sequences)
