from pathlib import Path
import toml
import fire

from ttsclient.utils.parseBoolArg import parse_bool_arg


# HERE = Path(__file__).parent.absolute()
HERE = Path("./")


def get_version():
    pyproject_path = "pyproject.toml"

    with open(pyproject_path, "r") as file:
        pyproject_data = toml.load(file)

    return pyproject_data["tool"]["poetry"]["version"]


def generate_version_file(alpha: bool = True):
    alpha = parse_bool_arg(alpha)
    version = get_version()
    if alpha:
        version += "-alpha"
    with open(HERE / "ttsclient" / "version.txt", "w") as f:
        f.write(version)
    with open(
        HERE / "web_front" / "assets" / "gui_settings" / "version.txt",
        "w",
    ) as f:
        f.write(version)


def main():
    fire.Fire(generate_version_file)
