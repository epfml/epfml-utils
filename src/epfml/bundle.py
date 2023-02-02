"""
Transfer code between machines through EPFL's S3 storage system,
and keep a permanent record of the code's state.

To exclude files from the package, you can add a `.codepack.toml` file to your directory:

```
exclude = [
    "__pycache__",
    "._*",
    ".ipynb_checkpoints",
    "core",
]

include = [
    "my_large_file.txt"  # would cause errors because it's larger than 100 KiB.
]
```
"""

import dataclasses
import datetime
import hashlib
import io
import pathlib
import tarfile
from typing import Union

import pathspec
import toml

import epfml.config

DEFAULT_EXCLUDE_LIST = [
    "__pycache__",
    "._*",
    ".AppleDouble",
    ".git",
    ".gitignore",
    ".ipynb_checkpoints",
    ".pylintrc",
    ".vscode",
    "*.exr",
    "*.pyc",
    "core",
]

DEFAULT_INCLUDE_LIST = []


@dataclasses.dataclass()
class Package:
    id: str
    contents: bytes


def tar_package(directory: Union[str, pathlib.Path] = ".") -> Package:
    directory = pathlib.Path(directory)

    config = {
        "exclude": DEFAULT_EXCLUDE_LIST,
        "include": DEFAULT_INCLUDE_LIST,
        "max_file_size": 100_000,
    }
    try:
        user_config = toml.load(directory / ".codepack.toml")
        config = {**config, **user_config}
    except FileNotFoundError as e:
        pass

    included_files = list(
        _filter_files(
            directory,
            exclude=config["exclude"],
            include=config["include"],
            max_size=config["max_file_size"],
        )
    )
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for file in included_files:
            tar.add(file, arcname=file.relative_to(directory))
    buffer.seek(0)

    basename = directory.resolve().name
    hash = _multi_file_sha1_hash(included_files)
    user = epfml.config.ldap
    date = datetime.datetime.now().strftime("%Y%m%d")
    package_id = f"{user}_{basename}_{date}_{hash[-8:]}"

    return Package(package_id, buffer.read())


def tar_extract(package: bytes, output_directory: Union[pathlib.Path, str]):
    with io.BytesIO(package) as buffer:
        with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
            tar.extractall(output_directory)


def _filter_files(
    directory: pathlib.Path,
    *,
    exclude: list[str],
    include: list[str],
    max_size: int,
):
    exclude_spec = pathspec.PathSpec.from_lines(
        pathspec.patterns.GitWildMatchPattern, exclude
    )
    include_spec = pathspec.PathSpec.from_lines(
        pathspec.patterns.GitWildMatchPattern, include
    )

    for file in directory.rglob("*"):
        if exclude_spec.match_file(file):
            continue
        if include_spec.match_file(file):
            yield file
            continue
        if file.stat().st_size > max_size:
            raise RuntimeError(
                f"The file {file} is suspiciously large.\n"
                "To include it, add it to `include` in `.codepack.toml`.\n"
                "To exclude it, add it to `exclude` in `.codepack.toml`."
            )
        yield file


def _multi_file_sha1_hash(files: list[pathlib.Path]):
    """Sha1-hash the contents of a number of files."""
    hash = hashlib.sha1()
    for file in files:
        if file.is_file():
            with open(file, "rb") as fh:
                hash.update(fh.read())
    return hash.hexdigest()
