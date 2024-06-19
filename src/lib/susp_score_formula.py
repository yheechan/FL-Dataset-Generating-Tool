import math

def measure_muse(features, total_p2f, total_f2p, mutant_key_list):
    utilized_mutant_cnt = 0
    line_total_p2f = 0
    line_total_f2p = 0

    final_muse_score = 0.0

    for p2f_m, f2p_m in mutant_key_list:
        p2f = features[p2f_m]
        f2p = features[f2p_m]

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
    tot_failing_tcs = features['# of totfailed_TCs']
    met_score_list = []

    for p2f_m, f2p_m in mutant_key_list:
        p2f = features[p2f_m]
        f2p = features[f2p_m]

        if p2f == -1 or f2p == -1:
            continue

        score = 0.0
        if f2p + p2f == 0:
            score = 0.0
        else:
            score = ((f2p) / math.sqrt(tot_failing_tcs * (f2p + p2f)))

        met_score_list.append(score)

    final_met_score = max(met_score_list)
    return final_met_score