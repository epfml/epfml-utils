# EPFML Utilities

Internal tools for the MLO lab of EPFL.

## Installation

```shell
❯ pip install epfml-utils
```

Add environment variables to your `~/.bashrc` or equivalent file:

```bash
export EPFML_STORE_S3_ACCESS_KEY=# Ask a friend.
export EPFML_STORE_S3_SECRET_KEY=# Ask a friend.
export EPFML_STORE_S3_ENDPOINT="https://s3.epfl.ch"
export EPFML_STORE_S3_BUCKET="13319-6af98428eae7a50adb5158685e34011d"
export EPFML_LDAP=# Your Gaspar username.
```

and make sure they are loaded:
```bash
source ~/.bashrc
echo $EPFML_LDAP  # Check if this prints your username.
```


## Key-value store

This key-value store can help to transfer information between machines.
Do not expect this to be fast or high-volume.
__Don't__ use this 100's of times in a training script.

### Command-line usage

On one machine:
```shell
❯ epfml store set my_name "Bob"
```
On any other machine:
```shell
❯ epfml store get my_name
Bob
```

### Python usage

```python
import torch
import epfml.store

epfml.store.set("my_data", {"name": "Bob", "lab": "MLO"})
epfml.store.set("tensor", torch.zeros(4))
```

```python
print(epfml.store.get("tensor"))
epfml.store.unset("tensor")
print(epfml.store.pop("my_data"))  # get and delete
```


## Transporting code between machines

### Packing

Upload a copy of the current working directory:

```shell
❯ epfml bundle pack
📦 Packaged and shipped.
⬇️ Unpack with `epfml bundle unpack mlotools_20230202_a205e830 -o .`.
```

To exclude (large / non-code) files from the package, add a config file to the directory

```shell
❯ epfml bundle init
📦 Default config file written to `/Users/vogels/epfl/mlotools/.epfml.bundle.toml`.
```

and customize it to your needs.

### Unpacking

You can download the code into a directory:

```shell
❯ epfml bundle unpack mlotools_20230202_a205e830 -o some_directory
```

Or you can run a training script, or any other shell command, in a temporary check-out of the package:

```shell
❯ epfml bundle exec mlotools_20230202_a205e830 -- du -sh
🏃 Running inside a tmp clone of package `mlotools_20230202_a205e830`.
160K    .
```

## Contributing

This repository is meant to be a collection of independent tools that each serve a simple well-defined purpose.

If you want to improve any of the tools in this repo, or contribute new tools. Take the following steps:

1. Clone this repository.
2. Initialize pre-commit: `cd epfml-utils && pre-commit install` (`pip install pre-commit`). This runs a couple of checks before you commit to keep this repo clean.
3. Ask someone else to scrutinize your contributions. They can help you to improve the API and catch bugs. You can also check these very nice [API design principles](https://github.com/google/etils/blob/main/docs/api-design.md) for tips.

To release a new version on PyPi, just increase the version number in `pyproject.yoml` and commit to Github.
