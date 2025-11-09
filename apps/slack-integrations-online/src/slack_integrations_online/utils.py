from pathlib import Path
import yaml


def load_yaml_file(config_path: Path):

    config = yaml.safe_load(config_path.read_text())
    config = config["parameters"]

    return config