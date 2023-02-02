"""
A key-value store based on EPFL's S3 storage.
This is a way to transmit information between different computers.
"""

import argparse
import contextlib
import datetime
import pickle
from typing import Any, Optional

import boto3
import botocore.exceptions

import mlotools.cli_utils as cli_utils
import mlotools.config as config


def set(
    key: str,
    value: Any,
    *,
    user: Optional[str] = None,
    ttl: Optional[datetime.timedelta],
):
    if user is None:
        user = config.default_user
    key = f"{user}/{key}"
    serialized_value = pickle.dumps(value)
    expires = datetime.datetime.now() + ttl if ttl is not None else ""
    _s3_bucket().put_object(Key=key, Body=serialized_value, Expires=expires)


def unset(
    key: str,
    *,
    user: Optional[str] = None,
):
    if user is None:
        user = config.default_user
    key = f"{user}/{key}"
    with _handle_missing_key_errors(key):
        _s3_bucket().delete_objects(Delete={"Objects": [{"Key": key}]})


def get(key: str, *, user: Optional[str] = None) -> Any:
    if user is None:
        user = config.default_user
    key = f"{user}/{key}"

    with _handle_missing_key_errors(key):
        serialized_value = _s3_bucket().Object(key).get()["Body"].read()
        return pickle.loads(serialized_value)


def main():
    with cli_utils.nicely_print_runtime_errors():
        parser = argparse.ArgumentParser()
        parser.add_argument("--user", "-u", type=str, default=config.default_user)

        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        getparser = subparsers.add_parser("get")
        getparser.add_argument("key", type=str)

        unsetparser = subparsers.add_parser("unset")
        unsetparser.add_argument("key", type=str)

        setparser = subparsers.add_parser("set")
        setparser.add_argument("key", type=str)
        setparser.add_argument("value", type=str)
        setparser.add_argument("--ttl-days", type=int)

        args = parser.parse_args()

        if args.subcommand == "get":
            print(get(args.key, user=args.user))
        elif args.subcommand == "set":
            ttl = (
                datetime.timedelta(days=args.ttl_days)
                if args.ttl_days is not None
                else None
            )
            set(args.key, args.value, user=args.user, ttl=ttl)
        elif args.subcommand == "unset":
            unset(args.key, user=args.user)


def _s3_bucket():
    s3 = boto3.resource(
        service_name="s3",
        aws_access_key_id=config.keyval_access_key,
        aws_secret_access_key=config.keyval_secret_key,
        endpoint_url=config.keyval_endpoint,
    )
    assert config.keyval_bucket is not None
    return s3.Bucket(config.keyval_bucket)


@contextlib.contextmanager
def _handle_missing_key_errors(key: str):
    try:
        yield
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":  # type: ignore
            raise RuntimeError(f"Key {key} not found.")
        else:
            raise


if __name__ == "__main__":
    main()
