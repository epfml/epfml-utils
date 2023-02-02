# EPFML Utilities

Internal tools for the MLO lab of EPFL.

## Installation

```shell
$ pip install epfml-utils
```

Add environment variables to your `~/.bashrc` or equivalent file:

```bash
export EPFML_STORE_S3_ACCESS_KEY = # Ask a friend.
export EPFML_STORE_S3_SECRET_KEY = # Ask a friend.
export EPFML_STORE_S3_ENDPOINT = "https://s3.epfl.ch"
export EPFML_STORE_S3_BUCKET = "13319-6af98428eae7a50adb5158685e34011d"
export EPFML_LDAP = # Your Gaspar username.
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
$ epfml store set my_name "Bob"
```
On any other machine:
```shell
$ epfml store get my_name
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
