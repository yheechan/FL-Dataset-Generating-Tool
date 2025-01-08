import argparse
import torch

from ml.postprocessor import Postprocessor
from ml.trainer import Trainer
from ml.inference import Inference

MBFL_METHOD = "for_random_mbfl"
# MBFL_METHOD = "for_sbfl_ranked_mbfl_desc"
MAX_LINES_FOR_RANDOM = 50
SBFL_RANKED_RATE = 0.30
SBFL_STANDARD = "gp13"
MUT_CNT_CONFIG = [2, 4, 6, 8, 10]
EXPERIMENT_REPEAT = 5
INCLUDE_CCT = False
APPLY_HEURISTIC = True
VERSIONS_TO_REMOVE = []
DELIBERATE_INCLUSION = True

def handle_feature_preparation(args):
    postprocessor = Postprocessor(
        args.subject, args.experiment_name
    )
    postprocessor.run()

def handle_train(args):
        # # Target dataset
        # if len(args.subject2setname_pair) == 0:
        #     print("Error: No subject2setname pair is provided.")
        #     print("Example: --subject2setname-pair jsoncpp:FL-dataset-jsoncpp-240803-v2 libxml2:FL-dataset-libxml2")
        #     exit(1)
        # pair_list = [pair.split(":") for pair in args.subject2setname_pair]

        # # Project name
        # if args.project_name == None:
        #     print("Error: Project name is not provided.")
        #     print("Example: --project-name FL-model-240803-v1")
        #     exit(1)
        # project_name = args.project_name

        # Train, validate, test ratio
        train_ratio, validate_ratio, test_ratio = args.train_validate_test_ratio
        if train_ratio + validate_ratio + test_ratio != 10:
            print("Error: Train, validate, test ratio must sum up to 10.")
            print("Example: --train-validate-test-ratio 6 2 2")
            exit(1)

        # device
        device = args.device
        if torch.cuda.is_available() and args.device == "cpu":
            device = "cuda"
        
        subject_name = args.subject
        experiment_name = args.experiment_name

        trainer = Trainer(
            # config param
            subject_name, experiment_name,
            train_ratio, validate_ratio, test_ratio,
            random_seed=args.random_seed,
            # training param
            epoch=args.epoch,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            device=device,
            # model param
            model_shape=args.model_shape, # 2024-08-08
            dropout=args.dropout,
        )
        trainer.run()

def handle_inference(args):
    # Target dataset
    if len(args.subject2setname_pair) == 0:
        print("Error: No subject2setname pair is provided.")
        print("Example: --subject2setname-pair jsoncpp:FL-dataset-jsoncpp-240803-v2 libxml2:FL-dataset-libxml2")
        exit(1)
    pair_list = [pair.split(":") for pair in args.subject2setname_pair]

    # Project name
    if args.project_name == None:
        print("Error: Project name is not provided.")
        print("Example: --project-name FL-model-240803-v1")
        exit(1)
    project_name = args.project_name

    # device
    device = args.device
    if torch.cuda.is_available() and args.device == "cpu":
        device = "cuda"
    
    # Inference name
    if args.inference_name == None:
        print("Error: Inference name is not provided.")
        print("Example: --inference-name libxml2-inference-v1")
        exit(1)
    
    inference = Inference(
        # config param
        project_name, pair_list,
        device, args.inference_name
    )
    inference.run()

def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.prepare_fl_features:
        handle_feature_preparation(args)
    elif args.train:
        handle_train(args)

    # if args.postprocess_fl_features == True:
    #     handle_postprocess(args)
    # elif args.train == True:
    #     handle_train(args)
    # elif args.inference == True:
    #      handle_inference(args)
        
        

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")

    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)

    
    # parser.add_argument("--subject2setname-pair", type=str, nargs="+", help="Subject name and its FL dataset directory file name pair(s). EX: jsoncpp:FL-dataset-jsoncpp-240803-v2 libxml2:FL-dataset-libxml2", required=True)

    # 1. Prepare FL features
    parser.add_argument("--prepare-fl-features", action="store_true", help="Prepare FL features.")

    # 2. Train the model
    parser.add_argument("--train", action="store_true", help="Train the model.")
    # config param
    parser.add_argument("--project-name", type=str, help="Project name.")
    parser.add_argument("--train-validate-test-ratio", type=int, nargs=3, help="Train, validate, test ratio. EX: 6 2 2")
    parser.add_argument("--random-seed", type=int, default=42, help="Random seed. Default is 42.")
    # training param
    parser.add_argument("--epoch", type=int, default=3, help="Epoch. Default is 3.")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size. Default is 64.")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate. Default is 1e-3.")
    parser.add_argument("--device", type=str, default="cpu", help="Device. Default is cpu.")
    # model param
    parser.add_argument("--dropout", type=float, default=0.2, help="Dropout. Default is 0.2.")
    parser.add_argument("--model-shape", type=int, nargs="+", default=[35, 512, 1024, 2048, 1024, 512, 1], help="Determine the input, hidden, and output size of model. Ex: 35 512 1024 2048 1024 512 1")

    # 3. Inference the model
    parser.add_argument("--inference", action="store_true", help="Inference the model.")
    parser.add_argument("--inference-name", type=str, help="Inference name.")


    return parser

if __name__ == "__main__":
    main()
