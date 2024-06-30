import json
import pandas as pd
import sys

# +++++++++++++++++++++
# ++++ MBFL UTILS  ++++
# +++++++++++++++++++++

met_key = "met susp. score"
muse_key = "muse susp. score"
mbfl_formulas = [met_key, muse_key]
bug_rank_key = "rank of buggy function (function level)"

def get_operator_from_mutant_info_file(mutant_info_file):
    with open(mutant_info_file, 'r') as f:
        lines = f.readlines()
        line = lines[2].strip()
        info = line.split(',')
        operator = info[1]
    return operator

def get_mutant_keys_as_pairs(max_mutants):
    mutant_keys = []
    for i in range(1, max_mutants+1):
        mutant_keys.append((f"m{i}:p2f", f"m{i}:f2p"))
    return mutant_keys

def get_mutant_keys(max_mutants):
    mutant_keys = []
    for i in range(1, max_mutants+1):
        mutant_keys.append(f'm{i}:f2p')
        mutant_keys.append(f'm{i}:p2f')
    return mutant_keys

def get_mutation_testing_results_form_data(version_dir, buggy_line_key):
    mutation_testing_results_csv = version_dir / 'mutation_testing_results.csv'

    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_lineno = buggy_line_key.split('#')[-1]

    mutants_data = {
        '# mutants': 0,
        '# uncompilable mutants': 0,
        '# mutans on buggy line': 0,
        '# uncompilable mutants on buggy line': 0,
        '# compilable mutants on buggy line': 0,
        'total_p2f': 0,
        'total_f2p': 0,
    }

    with open(mutation_testing_results_csv, 'r') as f:
        lines = f.readlines()

        for line in lines[1:]:
            mutants_data['# mutants'] += 1

            info = line.strip().split(',')
            target_file = info[0].split('/')[-1]
            mutant_id = info[1]
            mutant_lineno = info[2]
            num_of_failing_tcs_at_line = info[3]
            mutant_file_name = info[4]
            mutant_build_result = info[5]
            
            mutant_p2f = info[6]
            mutant_p2p = info[7]
            mutant_f2p = info[8]
            mutant_f2f = info[9]

            mutant_p2f_tcs = info[10]
            mutant_p2p_tcs = info[11]
            mutant_f2p_tcs = info[12]
            mutant_f2f_tcs = info[13]

            if mutant_build_result == 'FAIL':
                mutants_data['# uncompilable mutants'] += 1
            else:
                mutants_data['total_p2f'] += int(mutant_p2f)
                mutants_data['total_f2p'] += int(mutant_f2p)
            
            if target_file == buggy_target_file and mutant_lineno == buggy_lineno:
                mutants_data['# mutans on buggy line'] += 1

                if mutant_build_result == 'PASS':
                    mutants_data['# compilable mutants on buggy line'] += 1
                else:
                    mutants_data['# uncompilable mutants on buggy line'] += 1
    
    return mutants_data

def get_mbfl_rank_at_method_level(
        mbfl_features_csv_file,
        buggy_line_key,
        mbfl_formula,
        mutant_keys
):
    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_function_name = buggy_line_key.split('#')[1]
    buggy_lineno = int(buggy_line_key.split('#')[-1])

    mbfl_features_df = pd.read_csv(mbfl_features_csv_file)

    # 1. SET ALL BUGGY LINE OF BUGGY FUNCTION TO 1
    for index, row in mbfl_features_df.iterrows():
        key = row['key']
        target_file = key.split('#')[0].split('/')[-1]
        function_name = key.split('#')[1]
        line_num = int(key.split('#')[-1])

        # split key to target_file, function_name, line_num (individual column)
        mbfl_features_df.at[index, 'target_file'] = target_file
        mbfl_features_df.at[index, 'function_name'] = function_name
        mbfl_features_df.at[index, 'line_num'] = line_num

        # check if the row is one of the buggy lines of the buggy function
        if target_file == buggy_target_file and function_name == buggy_function_name:
            mbfl_features_df.at[index, 'bug'] = 1
        else:
            mbfl_features_df.at[index, 'bug'] = 0
    

    # 2. DROP THE KEY COLUMN
    mbfl_features_df = mbfl_features_df.drop(columns=['key'])
    # mbfl_features_df = mbfl_features_df[[
    #     'target_file', 'function_name', 'line_num',
    #     'met_1', 'met_2', 'met_3', 'met_4',
    #     'muse_a', 'muse_b', 'muse_c',
    #     'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse_5', 'muse_6',
    #     'bug'
    # ]]
    mbfl_features_df = mbfl_features_df[[
        'target_file', 'function_name', 'line_num',
        '# of totfailed_TCs', '#_failing_tcs_@line', '# of mutants'] + mutant_keys + [
        '|muse(s)|', 'total_f2p', 'total_p2f', 'line_total_f2p', 'line_total_p2f',
        'muse_1', 'muse_2', 'muse_3', 'muse_4',
        'muse susp. score', 'met susp. score', 'bug'

    ]]



    # 3. GROUP ROWS BY THE SAME FUNCTION NAME AND
    # APPLY THE VALUE OF THE LINE WITH THE HIGHEST MUSE_6 SCORE
    mbfl_features_df = mbfl_features_df.groupby(
        ['target_file', 'function_name']).apply(
            lambda x: x.nlargest(1, mbfl_formula)
        ).reset_index(drop=True)
    

    # 4. SORT THE ROWS BY THE FORMULA VALUE
    mbfl_features_df = mbfl_features_df.sort_values(by=[mbfl_formula], ascending=False).reset_index(drop=True)

    
    # 5. ADD A RANK COLUMN TO THE DF
    # THE RANK IS BASED ON FORMULA VALUE
    # IF THE RANK IS A TIE, THE RANK IS THE UPPER BOUND OF THE TIERS
    mbfl_features_df['rank'] = mbfl_features_df[mbfl_formula].rank(method='max', ascending=False).astype(int)
    # mbfl_features_df.to_csv('ranked-function-level.csv', index=False)


    # 6. GET THE RANK OF THE BUGGY LINE
    # AND THE MINIMUM RANK OF THE FORMULA
    # AND THE SCORE
    func_n = mbfl_features_df.shape[0]
    total_num_of_func = 0
    best_rank = sys.maxsize
    best_score = None
    bug_rank = -1
    bug_score = None

    for index, row in mbfl_features_df.iterrows():
        total_num_of_func += 1
        curr_rank = row['rank']
        curr_target_file = row['target_file']
        curr_function_name = row['function_name']
        curr_score = row[mbfl_formula]

        # assign the best rank number
        if curr_rank < best_rank:
            best_rank = curr_rank
            best_score = curr_score
        
        if curr_rank == best_rank:
            assert curr_score == best_score, f"score is not the same"


        # assign the rank of the buggy line
        if curr_target_file == buggy_target_file and \
            curr_function_name == buggy_function_name:
            bug_rank = curr_rank
            bug_score = curr_score
            assert row['bug'] == 1, f"bug is not 1"
        
    assert best_rank != 0, f"min_rank is 0"
    assert best_rank != sys.maxsize, f"min_rank is sys.maxsize"
    assert best_score is not None, f"best_score is None"

    assert bug_rank != -1, f"rank_bug is -1"
    assert bug_score is not None, f"bug_score is None"

    assert func_n == total_num_of_func, f"func_n != total_num_of_func"

    # print(formula, best_rank, best_score, bug_rank, bug_score)
    data = {
        f'# of functions': total_num_of_func,
        f'# of functions with same highest score': best_rank,
        f'score of highest rank': best_score,
        f'rank of buggy function (function level)': bug_rank,
        f'score of buggy function': bug_score
    }
    return data


# +++++++++++++++++++++
# ++++ SBFL UTILS  ++++
# +++++++++++++++++++++
def get_sbfl_rank_at_method_level(
        sbfl_features_csv_file,
        buggy_line_key,
        sbfl_formula
):
    key_info = buggy_line_key.split('#')
    # bug_version = key_info[0].strip()
    bug_target_file = key_info[0].strip()
    bug_function_name = key_info[1].strip()
    bug_line_num = int(key_info[2].strip())

    sbfl_features_df = pd.read_csv(sbfl_features_csv_file)

    # 1. SET ALL BUGGY LINE OF BUGGY FUNCTION TO BUG1
    for index, row in sbfl_features_df.iterrows():
        key = row['key']
        curr_key_info = key.split('#')
        # curr_version = curr_key_info[0].strip()
        curr_target_file = curr_key_info[0].strip()
        curr_function_name = curr_key_info[1].strip()
        curr_line_num = int(curr_key_info[2].strip())

        sbfl_features_df.at[index, 'target_file'] = curr_target_file
        sbfl_features_df.at[index, 'function_name'] = curr_function_name
        sbfl_features_df.at[index, 'line_num'] = curr_line_num

        # set all buggy lines of buggy function to bug 1
        if curr_target_file == bug_target_file and \
            curr_function_name == bug_function_name:
            sbfl_features_df.at[index, 'bug'] = 1
        else:
            sbfl_features_df.at[index, 'bug'] = 0

    # 2. DROP THE LINENO COLUMN
    sbfl_features_df.drop(columns=['key'])
    sbfl_features_df = sbfl_features_df[[
        'target_file', 'function_name', 'line_num',
        'ep', 'ef', 'np', 'nf',
        'Binary', 'GP13', 'Jaccard', 'Naish1',
        'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1',
        'bug'
    ]]
    # sbfl_features_df.to_csv('new1.csv', index=False)


    # 3. GROUP ROWS BY SAME FUNCTION NAME AND
    # APPLY VALUE OF THE LINE WITH THE HIGHEST VALUE OF THE FORMULA
    sbfl_features_df = sbfl_features_df.groupby(
        ['target_file', 'function_name']).apply(
            lambda x: x.nlargest(1, sbfl_formula)
        ).reset_index(drop=True)
    # sbfl_features_df.to_csv('new2.csv', index=False)

    

    # 4. SORT THE ROWS BY THE FORMULA VALUE
    sbfl_features_df = sbfl_features_df.sort_values(by=[sbfl_formula], ascending=False).reset_index(drop=True)
    # sbfl_features_df.to_csv('new3.csv', index=False)


    
    # 5. ADD A RANK COLUMN TO THE DF
    # THE RANK IS IN THE STANDARD OF FORMULA COLUMN
    # IF THE RANK IS A TIE, THE RANK IS THE UPPER BOUND OF THE TIE
    sbfl_features_df['rank'] = sbfl_features_df[sbfl_formula].rank(ascending=False, method='max').astype(int)
    # sbfl_features_df.to_csv('new4.csv', index=False)

    
    # 6. GET THE RANK OF THE BUGGY LINE
    # AND THE MINIMUM RANK OF THE FORMULA
    # AND THE SCORE
    func_n = sbfl_features_df.shape[0]
    total_num_of_func = 0
    best_rank = sys.maxsize
    best_score = None
    bug_rank = -1
    bug_score = None
    for index, row in sbfl_features_df.iterrows():
        total_num_of_func += 1
        curr_rank = row['rank']
        curr_target_file = row['target_file']
        curr_function_name = row['function_name']
        curr_score = row[sbfl_formula]

        # assign the best rank number
        if curr_rank < best_rank:
            best_rank = curr_rank
            best_score = curr_score
        
        if curr_rank == best_rank:
            assert curr_score == best_score, f"score is not the same"


        # assign the rank of the buggy line
        if curr_target_file == bug_target_file and \
            curr_function_name == bug_function_name:
            bug_rank = curr_rank
            bug_score = curr_score
            assert row['bug'] == 1, f"bug is not 1"

    assert best_rank != 0, f"min_rank is 0"
    assert best_rank != sys.maxsize, f"min_rank is sys.maxsize"
    assert best_score is not None, f"best_score is None"

    assert bug_rank != -1, f"rank_bug is -1"
    assert bug_score is not None, f"bug_score is None"

    assert func_n == total_num_of_func, f"func_n != total_num_of_func"

    # print(formula, best_rank, best_score, bug_rank, bug_score)
    data = {
        f'total # of functions': total_num_of_func,
        f'# of functions with same highest {sbfl_formula} score': best_rank,
        f'{sbfl_formula} score of highest rank': best_score,
        f'rank of buggy function ({sbfl_formula})': bug_rank,
        f'{sbfl_formula} score of buggy function': bug_score
    }
    return data