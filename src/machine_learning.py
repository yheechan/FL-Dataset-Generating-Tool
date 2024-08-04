import argparse
import torch

from ml.postprocessor import Postprocessor
from ml.trainer import Trainer

def handle_postprocess(args):
        if len(args.subject2setname_pair) == 0:
            print("Error: No subject2setname pair is provided.")
            print("Example: --subject2setname-pair jsoncpp:FL-dataset-jsoncpp-240803-v2 libxml2:FL-dataset-libxml2")
            exit(1)
        pair_list = [pair.split(":") for pair in args.subject2setname_pair]
        
        for subject, set_name in pair_list:
            print(f"Postprocessing FL features for {subject}...")
            postprocessor = Postprocessor(subject, set_name)
            postprocessor.run()
            print()

def handle_train(args):
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
        
        # stack size
        if args.stack_size < 2:
            print("Error: Stack size has to be greater than 2.")
            exit(1)
        
        trainer = Trainer(
            # config param
            project_name, pair_list,
            train_ratio, validate_ratio, test_ratio,
            random_seed=args.random_seed,
            # training param
            epoch=args.epoch,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            device=device,
            # model param
            input_size=args.input_size,
            hidden_size=args.hidden_size,
            dropout=args.dropout,
            stack_size=args.stack_size,
            output_size=args.output_size
        )
        trainer.run()


def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.postprocess_fl_features == True:
        handle_postprocess(args)
    elif args.train == True:
        handle_train(args)
        
        

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject2setname-pair", type=str, nargs="+", help="Subject name and its FL dataset directory file name pair(s). EX: jsoncpp:FL-dataset-jsoncpp-240803-v2 libxml2:FL-dataset-libxml2", required=True)

    parser.add_argument("--postprocess-fl-features", action="store_true", help="Formulate FL dataset with features for machine learning.")

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
    parser.add_argument("--input-size", type=int, default=35, help="Input size. Default is 35.")
    parser.add_argument("--hidden-size", type=int, default=64, help="Hidden size. Default is 64.")
    parser.add_argument("--dropout", type=float, default=0.2, help="Dropout. Default is 0.2.")
    parser.add_argument("--stack-size", type=int, default=3, help="Stack size (has to be > 2). Default is 3.")
    parser.add_argument("--output-size", type=int, default=1, help="Output size. Default is 1.")

    return parser

if __name__ == "__main__":
    main()
