import math

# ++++++++++++++++++++++++++
# +++++ measuring MBFL +++++
# ++++++++++++++++++++++++++

def return_f2p_p2f_values(feature, p2f_m, f2p_m):
    if type(feature[p2f_m]) == str or type(feature[f2p_m]) == str:
        if feature[p2f_m] == "-1" or feature[f2p_m] == "-1":
            p2f = -1
            f2p = -1
        else:
            p2f = int(feature[p2f_m])
            f2p = int(feature[f2p_m])
    else:
        p2f = feature[p2f_m]
        f2p = feature[f2p_m]

    return p2f, f2p

def measure_muse(features, total_p2f, total_f2p, mutant_key_list):
    utilized_mutant_cnt = 0
    line_total_p2f = 0
    line_total_f2p = 0

    final_muse_score = 0.0

    for p2f_m, f2p_m in mutant_key_list:
        p2f, f2p = return_f2p_p2f_values(features, p2f_m, f2p_m)

        if p2f == -1 or f2p == -1:
            continue

        utilized_mutant_cnt += 1
        line_total_p2f += p2f
        line_total_f2p += f2p

    muse_1 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1)))
    muse_2 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1)))

    muse_3 = muse_1 * line_total_f2p
    muse_4 = muse_2 * line_total_p2f

    final_muse_score = muse_3 - muse_4

    muse_data = {
        '|muse(s)|': utilized_mutant_cnt,
        'total_f2p': total_f2p,
        'total_p2f': total_p2f,
        'line_total_f2p': line_total_f2p,
        'line_total_p2f': line_total_p2f,
        'muse_1': muse_1,
        'muse_2': muse_2,
        'muse_3': muse_3,
        'muse_4': muse_4,
        'muse susp. score': final_muse_score
    }

    return muse_data

def measure_metallaxis(features, mutant_key_list):
    if type(features['# of totfailed_TCs']) == str:
        tot_failing_tcs = int(features['# of totfailed_TCs'])
    else:
        tot_failing_tcs = features['# of totfailed_TCs']

    met_score_list = []

    for p2f_m, f2p_m in mutant_key_list:
        p2f, f2p = return_f2p_p2f_values(features, p2f_m, f2p_m)

        if p2f == -1 or f2p == -1:
            continue

        score = 0.0
        if f2p + p2f == 0:
            score = 0.0
        else:
            score = ((f2p) / math.sqrt(tot_failing_tcs * (f2p + p2f)))

        met_score_list.append(score)

    if len(met_score_list) == 0:
        return 0.0
    final_met_score = max(met_score_list)
    return final_met_score


# ++++++++++++++++++++++++++
# +++++ measuring SBFL +++++
# ++++++++++++++++++++++++++
def calculate_spectrum(line, tc_list):
    executed = 0
    not_executed = 0

    for tc in tc_list:
        tc_name = tc.split('.')[0]
        if line[tc_name] == '1':
            executed += 1
        else:
            not_executed += 1
    
    return executed, not_executed

sbfl_formulas = [
    "Binary", "GP13", "Jaccard", "Naish1",
    "Naish2", "Ochiai", "Russel+Rao", "Wong1"
]

pp_sbfl_formulas = [
    "ER1a", "ER5a", "ER5c", "ER1b", "ER5b",
    "Ochiai", "Jaccard", "AMPLE",
    "Hamannn", "Dice", "M1", "M2", 
    "Hamming", "Goodman", "Euclid",
    "Wong1", "Wong2",
    "GP2", "GP3", "GP13", "GP19",
    "Tarantula", "Russel+Rao",
]

def sbfl(e_p, e_f, n_p, n_f, formula="Ochiai", fails=0, passes=0):
    if formula == "Jaccard":
        denominator = e_f + n_f + e_p
        if denominator == 0:
            return 0
        return e_f / denominator
    elif formula == "Binary":
        if 0 < n_f:
            return 0
        elif n_f == 0:
            return 1
    elif formula == "GP13":
        denominator = 2*e_p + e_f
        if denominator == 0:
            return 0
        return e_f + (e_f / denominator)
    elif formula == "Naish1":
        if 0 < n_f:
            return -1
        elif 0 == n_f:
            return n_p
    elif formula == "Naish2":
        x = e_p / (e_p + n_p + 1)
        return e_f - x
    elif formula == "Ochiai":
        denominator = math.sqrt((e_f + n_f) * (e_f + e_p))
        if denominator == 0:
            return 0
        return e_f / denominator
    elif formula == "Russel+Rao":
        return e_f/(e_p + n_p + e_f + n_f)
    elif formula == "Wong1":
        return e_f
    elif formula == "ER1a":
        if n_f > 0:
            return -1
        else:
            return n_p
    elif formula == "ER5a":
        return (e_f - ((e_f) / (e_p + n_p + 1)))
    elif formula == "ER5c":
        if e_f < fails:
            return 0
        else:
            return e_p
    elif formula == "ER1b":
        denominator = e_p + n_p + 1
        if denominator == 0:
            return 0
        return e_f - (e_p / denominator)
    elif formula == "ER5b":
        denominator = e_f + n_f + e_p + n_p
        if denominator == 0:
            return 0
        return e_f / denominator
    elif formula == "AMPLE":
        a = e_f / fails
        b = e_p / passes
        c = a - b
        return abs(c)
    elif formula == "Hamannn":
        numerator = e_f + n_p + e_p + n_f
        denominator = passes + fails
        if denominator == 0:
            return 0
        return numerator / denominator
    elif formula == "Dice":
        numerator = 2*e_f
        denominator = e_f + e_p + n_f
        if denominator == 0:
            return 0
        return numerator / denominator
    elif formula == "M1":
        numerator = e_f + n_p
        denominator = e_f + e_p
        if denominator == 0:
            return 0
        return numerator / denominator
    elif formula == "M2":
        numerator = e_f
        denominator = e_f + n_p + 2*n_f + 2*e_p
        if denominator == 0:
            return 0
        return numerator / denominator
    elif formula == "Hamming":
        return e_f + n_p
    elif formula == "Goodman":
        numerator = 2*e_f - n_f - e_p
        denominator = 2*e_f + n_f + e_p
        if denominator == 0:
            return 0
        return numerator / denominator
    elif formula == "Euclid":
        return math.sqrt(e_f + n_p)
    elif formula == "Wong2":
        return e_f - e_p
    elif formula == "GP2":
        a = e_f
        b = math.sqrt(e_p + n_p)
        c = math.sqrt(e_p)
        return 2 * (a + b) + c
    elif formula == "GP3":
        a = e_f ** 2
        b = math.sqrt(e_p)
        c = abs(a - b)
        return math.sqrt(c)
    elif formula == "GP19":
        a = e_p - e_f + fails + passes
        b = abs(a)
        return e_f * math.sqrt(b)
    elif formula == "Tarantula":
        a_numerator = e_f
        a_denominator = e_f + n_f
        a = 0
        if a_denominator != 0:
            a = a_numerator / a_denominator
        
        b_numerator = e_f
        b_denominator = e_f + n_f
        b = 0
        if b_denominator != 0:
            b = b_numerator / b_denominator
        
        c_numerator = e_p
        c_denominator = e_p + n_p
        c = 0
        if c_denominator != 0:
            c = c_numerator / c_denominator
        
        numerator = a
        denominator = b + c
        if denominator == 0:
            return 0
        return numerator / denominator
    else:
        raise Exception(f"Unknown formula: {formula}")
