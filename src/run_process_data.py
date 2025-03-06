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
        "zlib_ng_TF_top30",
        "libxml2_TF_top30",
        "opencv_features2d_TF_top30",
        "opencv_imgproc_TF_top30",
        "opencv_core_TF_top30",
        "jsoncpp_TF_top30",
        "opencv_calib3d_TF_top30"
    ]

    command_sequences = [
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "all_fails",
            "line_selection_rate": 100.0,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "rand",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.3,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish210-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.1,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish201-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.01,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish200-maxMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.0,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reducedAvg-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "reduced_num_mut",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reducedSbflnaish2-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "sbfl",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reducedMinMutants-excludeCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [2, 2, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [2],
            "experiment_repeat": 1,
            "include_cct": False,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }],
        ["time python3 analyzer.py --subject subject_name_here --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-maxMutants-withCCT", {
            "list_of_line_selection_methods": ["all_fails", "rand", "sbfl"],
            "line_selection_method": "sbfl",
            "line_selection_rate": 0.5,
            "list_of_mutant_num_methods": ["all_fails", "reduced_num_mut", "sbfl"],
            "mutant_num_method": "all_fails",
            "mutant_num_std": [10, 6, 2],
            "sbfl_standard": "naish2_5",
            "mut_cnt_config": [10],
            "experiment_repeat": 1,
            "include_cct": True,
            "apply_heuristic": False,
            "versions_to_remove": [],
            "deliberate_inclusion": False
        }]
    ]
    
    execute_commands(subjects, command_sequences)
