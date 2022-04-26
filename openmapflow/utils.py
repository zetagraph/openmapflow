from typing import Dict, Tuple
import numpy as np
import random
from pathlib import Path
import subprocess
import os
import yaml

try:
    import torch

    TORCH_INSTALLED = True
except ImportError:
    TORCH_INSTALLED = False


def set_seed(seed: int = 42):
    np.random.seed(seed)
    random.seed(seed)
    if TORCH_INSTALLED:
        torch.manual_seed(seed)


def get_dvc_dir(dvc_dir_name: str) -> Path:
    # TODO: Encode the authentication here

    dvc_dir = Path(__file__).parent.parent / f"data/{dvc_dir_name}"
    if not dvc_dir.exists():
        subprocess.run(["dvc", "pull", f"data/{dvc_dir_name}"], check=True)
        if not dvc_dir.exists():
            raise FileExistsError(f"{str(dvc_dir)} was not found.")
        if not any(dvc_dir.iterdir()):
            raise FileExistsError(f"{str(dvc_dir)} should not be empty.")
    return dvc_dir


def get_config(project_root: Path = Path(os.getcwd())) -> dict:
    config_path = project_root / "openmapflow.yaml"
    if not config_path.exists():
        raise FileExistsError(
            f"{str(config_path)} was not found in: {project_root}. You may need to pass project_root explicitly."
        )
    with config_path.open() as f:
        return yaml.safe_load(f)


def get_paths(project_root: Path = Path(os.getcwd())) -> Dict[str, Path]:
    config = get_config(project_root=project_root)
    return {k: project_root / f"data/{p}" for k, p in config["data_paths"].items()}


def find_nearest(array, value: float) -> Tuple[float, int]:
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    haversince formula, inspired by:
    https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude/41337005
    """
    p = 0.017453292519943295
    a = (
        0.5
        - np.cos((lat2 - lat1) * p) / 2
        + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    )
    return 12742 * np.arcsin(np.sqrt(a))


def distance_point_from_center(lat_idx: int, lon_idx: int, tif) -> int:
    x_dist = np.abs((len(tif.x) - 1) / 2 - lon_idx)
    y_dist = np.abs((len(tif.y) - 1) / 2 - lat_idx)
    return x_dist + y_dist