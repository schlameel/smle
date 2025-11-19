import argparse
from pathlib import Path
import urllib.request

SMLE_EMPTY_CONFIG_TEMPLATE = """\
project: example

# Training configuration
training:
  device: cpu
  seed: 42
  epochs: 10
  learning_rate: 1e-4
  weight_decay: 1e-2
  train_batch: 32
  test_batch: 32

# Logging
logger:
  dir: logger
  use_wandb: False

# Weights & Biases configuration
# wandb:
#   key: [your_wandb_key]
#   entity: [your_wandb_account]
"""

SMLE_MLP_CONFIG_TEMPLATE = """\
project: example

# Dataset settings
dataset:
  train_file: dataset/mnist_test.csv
  test_file: dataset/mnist_train.csv

# Training configuration
training:
  device: cpu
  export_dir: models
  seed: 42
  epochs: 10
  learning_rate: 1e-4
  weight_decay: 1e-2
  train_batch: 32
  test_batch: 32

# Logging
logger:
  dir: logger
  use_wandb: False

# Weights & Biases configuration
# wandb:
#   key: [your_wandb_key]
#   entity: [your_wandb_account]
"""


EMPTY_SCRIPT_TEMPLATE = """\
from smle.utils import set_seed
from smle import smle


@smle
def main(args):


    set_seed(args["training"]["seed"])


    # TODO: add your code here



if __name__ == "__main__":
    main()
"""


MLP_SCRIPT_TEMPLATE = """\
from smle.utils import set_seed
from smle.trainer import Trainer
from smle import smle


import pandas as pd


import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


from sklearn.metrics import confusion_matrix, classification_report


class CustomMLP(nn.Module):


    def __init__(self):
        super().__init__()


        self._in_h1 = nn.Linear(784, 128)
        self._h1_h2 = nn.Linear(128, 64)
        self._h2_out = nn.Linear(64, 10)


    def forward(self, x):
        x = F.relu(self._in_h1(x))
        x = F.relu(self._h1_h2(x))
        x = self._h2_out(x)
        return x


class CustomDataset(Dataset):


    def __init__(self, X, y):


        super().__init__()
        self._X = X
        self._y = y


    def __len__(self):
        return len(self._X)


    def __getitem__(self, index):


        x = torch.tensor(self._X[index], dtype=torch.float)
        y = torch.tensor(self._y[index], dtype=torch.long) # Cross Entropy requires long


        return x, y


@smle
def main(args):


    set_seed(args["training"]["seed"])


    df_train = pd.read_csv(args["dataset"]["train_file"])
    df_test = pd.read_csv(args["dataset"]["test_file"])


    X_train = df_train.iloc[:, 1:].values
    y_train = df_train.iloc[:, 0].values


    X_test = df_test.iloc[:, 1:].values
    y_test = df_test.iloc[:, 0].values


    train_dataset = CustomDataset(X_train, y_train)
    test_dataset = CustomDataset(X_test, y_test)


    train_loader = DataLoader(train_dataset, batch_size=args["training"]["train_batch"], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args["training"]["test_batch"], shuffle=False)


    device = args["training"]["device"]


    model = CustomMLP()
    loss_fn = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(),
                            lr=float(args["training"]["learning_rate"]),
                            weight_decay=float(args["training"]["weight_decay"]))


    trainer = Trainer(model, loss_fn, optimizer, device=args["training"]["device"])


    model = trainer.fit(train_loader=train_loader,
                        epochs=args["training"]["epochs"],
                        export_dir=args["training"]["export_dir"])


    predictions = []
    grounds = []


    model.eval()
    for data,labels in test_loader:


        data = data.to(device)


        probs = model(data).squeeze()
        preds = torch.argmax(probs, axis=1)


        predictions.extend(preds.detach().cpu().tolist())
        grounds.extend(labels.detach().cpu().tolist())


    print(f"{classification_report(grounds, predictions)}")
    print(f"{confusion_matrix(grounds, predictions)}")


if __name__ == "__main__":
    main()
"""
def cmd_init(args: argparse.Namespace) -> None:
    root = Path(args.path).resolve()


    if root.exists() and any(root.iterdir()) and not args.force:
        raise SystemExit(
            f"Refusing to init non-empty directory: {root}. Use --force to override."
        )


    root.mkdir(parents=True, exist_ok=True)


    # Folders
    (root / "logger").mkdir(exist_ok=True)


    # Config
    config_path = root / "smle.yaml"
    if config_path.exists() and not args.force:
        raise SystemExit("smle.yaml already exists; use --force to overwrite.")
    config_path.write_text(SMLE_EMPTY_CONFIG_TEMPLATE)


    # Example training script
    train_path = root / "main.py"
    if not train_path.exists() or args.force:
        train_path.write_text(EMPTY_SCRIPT_TEMPLATE)


    print(f"Initialized smle project in {root}")


def cmd_mlp_init(args: argparse.Namespace) -> None:
    root = Path(args.path).resolve()


    if root.exists() and any(root.iterdir()) and not args.force:
        raise SystemExit(
            f"Refusing to init non-empty directory: {root}. Use --force to override."
        )


    root.mkdir(parents=True, exist_ok=True)


    # Folders
    for sub in ("logger", "dataset", "models"):
        (root / sub).mkdir(exist_ok=True)


    # Download data
    print("Downloading MNIST dataset...")
    train_url = "https://pjreddie.com/media/files/mnist_train.csv"
    test_url = "https://pjreddie.com/media/files/mnist_test.csv"
    urllib.request.urlretrieve(train_url, root / "dataset" / "mnist_train.csv")
    urllib.request.urlretrieve(test_url, root / "dataset" / "mnist_test.csv")
    print("Download complete.")


    # Config
    config_path = root / "smle.yaml"
    if config_path.exists() and not args.force:
        raise SystemExit("smle.yaml already exists; use --force to overwrite.")
    config_path.write_text(SMLE_MLP_CONFIG_TEMPLATE)


    # Example training script
    train_path = root / "main.py"
    if not train_path.exists() or args.force:
        train_path.write_text(MLP_SCRIPT_TEMPLATE)


    print(f"Initialized smle project in {root}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="smle")
    subparsers = parser.add_subparsers(dest="command")


    # init subcommand
    p_init = subparsers.add_parser("init", help="Initialize an empty smle project")
    p_init.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if needed",
    )
    p_init.set_defaults(func=cmd_init)


    # init mlp subcommand
    p_init = subparsers.add_parser("mlp", help="Initialize a MLP smle project")
    p_init.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if needed",
    )


    p_init.set_defaults(func=cmd_mlp_init)


    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
