import builtins
from typing import Optional, TextIO
import os
from datetime import datetime
import wandb

_builtin_print = builtins.print
_log_file: str | None = None      # global log file path
_use_wandb: bool = False

_wandb_session = None

# ============================ #

def enable_smle_print() -> None:
    builtins.print = _log_print  # type: ignore[assignment]

def disable_smle_print() -> None:
    builtins.print = _builtin_print  # type: ignore[assignment]

def _log_print(*objects: object, sep: str = " ", end: str = "\n", file: Optional[TextIO] = None, flush: bool = False) -> None:
    """Log to file with timestamp and echo to stdout (mimicking built-in print signature)."""

    message = sep.join(map(str, objects))

    # Log to file
    if _log_file is not None:
        timestamp = datetime.now().replace(microsecond=0).isoformat(sep=" ")
        log_line = f"[{timestamp}] {message}\n"
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(log_line)

    # Pass all original arguments (including file/flush) to the real print
    _builtin_print(*objects, sep=sep, end=end, file=file, flush=flush)

# ============================== #

def init_logging_module(args: dict) -> None:

    builtins.print = _log_print

    export_dir = args["logger"]["dir"]
    os.makedirs(export_dir, exist_ok=True)

    filename = f'{args["project"]}.log'
    global _log_file
    _log_file = os.path.join(export_dir, filename)

    # truncate log
    with open(_log_file, "w", encoding="utf-8") as f:
        f.write("")

    for k, v in _flatten_dict(args).items():
        print(f"{k}: {v}")

    if "use_wandb" in args["logger"]:
        if args["logger"]["use_wandb"]:

            global _use_wandb
            _use_wandb = True
            _start_wandb_session(
                key=args["wandb"]["key"],
                entity=args["wandb"]["entity"],
                project=args["project"],
                config=args["training"],
            )


def close_logging_module():

    builtins.print = _builtin_print

    if _use_wandb and _wandb_session:
        _wandb_session.finish()

# ========================== #

def _start_wandb_session(
    key: str,
    entity: str,
    project: str,
    config,
) -> None:
    os.environ["WANDB_API_KEY"] = key

    global _wandb_session
    _wandb_session = wandb.init(
        entity=entity,
        project=project,
        config=config,
    )

def _flatten_dict(d: dict, parent_key: str = "", sep: str = "/") -> dict:
    """Flatten nested dictionary into a single-level dict with sep-joined keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)