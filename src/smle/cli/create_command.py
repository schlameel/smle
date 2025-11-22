import argparse
from pathlib import Path
from importlib.resources import files
from colorama import Fore, Style
import sys
import os

def execute(args: argparse.Namespace) -> None:

    root_dir = Path(args.path).resolve()
    root_dir.mkdir(parents=True, exist_ok=True)

    # Get the path to the 'templates' folder relative to the current package
    templates_path = files(__package__).joinpath('templates')

    if args.filetype == "yaml":
        config_path = root_dir / "smle.yaml"
        with open(templates_path/"smle.yaml", "r") as f:
            config_template = f.read()
        config_path.write_text(config_template)

        print(f"{Fore.GREEN}[SMLE] Initialized {Fore.LIGHTYELLOW_EX}{args.filetype}{Fore.GREEN} file in {Fore.LIGHTYELLOW_EX}{root_dir}{Fore.GREEN} directory.{Style.RESET_ALL}")

    else:

        print(f"{Fore.RED}[SMLE] Template not found for filetype {Fore.LIGHTYELLOW_EX}{args.filetype}{Fore.RED}.{Style.RESET_ALL}")
        sys.exit(1)

