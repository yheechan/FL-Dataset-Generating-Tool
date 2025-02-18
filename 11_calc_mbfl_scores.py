from pathlib import Path
import json
from matplotlib import pyplot as plt

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


# analysis_types = [
#     "allfails-excludeCCT-noHeuristics",
#     "rand50-excludeCCT-noHeuristics",
#     "sbflnaish250-excludeCCT-noHeuristics",
# ]

# plot a bar chart where
# y-axis is Avg. time duration for MBFL extraction in hours
# x axis is subject, each subject has 3 bars for each analysis type
# all the bars on analysis type must be the same color

# first make the dictionary for the data
time_data = {}
for subject in subjects:
    subject_name = "_".join(subject.split("_")[:2])
    if subject_name == "opencv_calib3d":
        subject_name = "*opencv_calib3d"

    time_data[subject_name] = {}
    for analysis_type in analysis_types:
        analysis_type_name = ""
        if analysis_type == "allfails-excludeCCT-noHeuristics":
            analysis_type_name = "all-lines"
        elif analysis_type == "rand50-excludeCCT-noHeuristics":
            analysis_type_name = "random"
        elif analysis_type == "sbflnaish250-excludeCCT-noHeuristics":
            analysis_type_name = "sbfl-based"
        
        time_data[subject_name][analysis_type_name] = results[subject][analysis_type]["10"]["avg_time_duration"]

# plot the bar chart
fig, ax = plt.subplots()

bar_width = 0.2
index = range(len(subjects))
colors = ['dimgray', 'silver', 'lime']

for i, analysis_type in enumerate(["all-lines", "random", "sbfl-based"]):
    avg_time_durations = [time_data[subject][analysis_type] for subject in time_data]
    ax.bar([p + bar_width * i for p in index], avg_time_durations, bar_width, label=analysis_type, color=colors[i])

ax.set_xlabel('Subject')
ax.set_ylabel('Avg. time taken (hours)')
ax.set_title('Avg. time taken for MBFL extraction by each line selection method')
ax.set_xticks([p + bar_width for p in index])
ax.set_xticklabels(time_data, rotation=45, ha="right")
ax.legend()

plt.tight_layout()

# save to file
plt.savefig(main_dir / "mbfl_time_duration.png")