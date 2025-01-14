from pathlib import Path
import subprocess as sp
import argparse

src_file = Path(__file__).resolve()
src_dir = src_file.parent


DATASET_DICT = {
    "D1": {
        "subject": "opencv_features2d_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "rand50-excludeCCT-noHeuristics-delibIncl",
    },
    "D2": {
        "subject": "opencv_features2d_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "rand50-excludeCCT-noHeuristics-noDelibIncl",
    },
    "D3": {
        "subject": "opencv_features2d_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "sbflgp13-excludeCCT-noHeuristics-delibIncl",
    },
    "D4": {
        "subject": "opencv_features2d_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "sbflgp13-excludeCCT-noHeuristics-noDelibIncl",
    },
    "D5": {
        "subject": "zlib_ng_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "rand50-excludeCCT-noHeuristics-delibIncl",
    },
    "D6": {
        "subject": "zlib_ng_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "rand50-excludeCCT-noHeuristics-noDelibIncl",
    },
    "D7": {
        "subject": "zlib_ng_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "sbflgp13-excludeCCT-noHeuristics-delibIncl",
    },
    "D8": {
        "subject": "zlib_ng_TF_top30",
        "experiment_name": "TF_top30",
        "targeting_experiment_name": "sbflgp13-excludeCCT-noHeuristics-noDelibIncl",
    },
}


def make_parser():
    parser = argparse.ArgumentParser(description="Script for ML analysis")

    parser.add_argument(
        "--model-name", type=str, help="Model name", required=True
    )
    parser.add_argument(
        "--model-id", type=str, help="Model ID", required=True
    )

    return parser



def main():
    parser = make_parser()
    args = parser.parse_args()

    for dataset_name, dataset_dict in DATASET_DICT.items():
        print(f"Start ML analysis for {dataset_name}")
        target_dataset_name = dataset_name
        if args.model_id in target_dataset_name:
            target_dataset_name = f"self-{target_dataset_name}"
            continue

        cmd = [
            "python3",
            "machine_learning.py",
            "--subject", dataset_dict["subject"],
            "--experiment-name", dataset_dict["experiment_name"],
            "--targeting-experiment-name", dataset_dict["targeting_experiment_name"],
            "--inference-name", target_dataset_name,
            "--inference",
            "--model-name", args.model_name,
            "--device", "cuda"
        ]
        print(cmd)
        res = sp.run(cmd, cwd=src_dir)
        print(f"Running command: {cmd}")
        print(f"Finished ML analysis for {dataset_name}")

    








if __name__ == "__main__":
    main()