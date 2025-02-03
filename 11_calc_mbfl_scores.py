from pathlib import Path
import json

curr_file = Path(__file__).resolve()
main_dir = curr_file.parent
out_dir = main_dir / "out"

subjects = [
    "zlib_ng_TF_top30",
    "libxml2_TF_top30",
    "opencv_features2d_TF_top30",
    "opencv_imgproc_TF_top30",
    "opencv_core_TF_top30",
    "opencv_calib3d_TF_top30"
]

analysis_types = [
    "allfails-excludeCCT-noHeuristics",
    "rand50-excludeCCT-noHeuristics",
    "sbflnaish250-excludeCCT-noHeuristics",
]

results = {}

# SUBJECT
for subject in subjects:
    analysis_dir = out_dir / subject / "analysis"

    if subject not in results:
        results[subject] = {}

    # ANALYSIS TYPE
    for analysis_type in analysis_types:

        if analysis_type not in results[subject]:
            results[subject][analysis_type] = {}

        analysis_type_dir = analysis_dir / analysis_type
        
        mbfl_overall_data_json = analysis_type_dir / "mbfl_overall_data.json"
        mbfl_overall_data = json.loads(mbfl_overall_data_json.read_text())

        # MUTATION # CONFIGURATION: 10
        for key, data in mbfl_overall_data.items():
            met_acc5 = 0
            met_acc10 = 0
            muse_acc5 = 0
            muse_acc10 = 0

            list_time_duration = []

            # VERSION
            for version_name, version_data in data.items():
                met_rank = version_data[0]["met_rank"]
                muse_rank = version_data[0]["muse_rank"]

                tot_build_time = version_data[0]["total_build_time"]
                tot_tc_exec_time = version_data[0]["total_tc_execution_time"]
                total_time_duration = (tot_build_time + tot_tc_exec_time) / 3600
                list_time_duration.append(total_time_duration)

                if met_rank <= 5:
                    met_acc5 += 1
                if met_rank <= 10:
                    met_acc10 += 1
                if muse_rank <= 5:
                    muse_acc5 += 1
                if muse_rank <= 10:
                    muse_acc10 += 1

            met_acc5 /= len(data)
            met_acc10 /= len(data)
            muse_acc5 /= len(data)
            muse_acc10 /= len(data)
            avg_time_duration = sum(list_time_duration) / len(list_time_duration)

            results[subject][analysis_type][key] = {
                "met_acc5": met_acc5,
                "met_acc10": met_acc10,
                "muse_acc5": muse_acc5,
                "muse_acc10": muse_acc10,
                "avg_time_duration": avg_time_duration
            }

# write results to csv file
out_file = main_dir / "mbfl_scores.csv"
with open(out_file, "w") as f:
    f.write("subject,analysis_type,num_mutants,avg. time duration,met_acc5,met_acc10,muse_acc5,muse_acc10\n")
    for subject in subjects:
        for analysis_type in analysis_types:
            for key, data in results[subject][analysis_type].items():
                # round to 2 decimal places
                data['met_acc5'] = round((data['met_acc5'])*100, 2)
                data['met_acc10'] = round((data['met_acc10'])*100, 2)
                data['muse_acc5'] = round((data['muse_acc5'])*100, 2)
                data['muse_acc10'] = round((data['muse_acc10'])*100, 2)
                f.write(f"{subject},{analysis_type},{key},{data['avg_time_duration']},{data['met_acc5']},{data['met_acc10']},{data['muse_acc5']},{data['muse_acc10']}\n")

