"""
A key-value store based on EPFL's S3 storage.
This is a way to transmit information between different computers.
"""

import contextlib
import pickle
from typing import Any, Optional, Protocol

import boto3
import botocore.exceptions

import epfml.config as config


def set(
    key: str,
    value: Any,
    *,
    user: Optional[str] = None,
):
    if user is None:
        user = config.ldap

    key = f"{user}/{key}"

    serialized_value = pickle.dumps(value)
    _s3_bucket().put_object(Key=key, Body=serialized_value)


def get(
    key: str,
    *,
    user: Optional[str] = None,
) -> Any:
    if user is None:
        user = config.ldap
    key = f"{user}/{key}"

    with _handle_missing_key_errors(key):
        serialized_value = _s3_bucket().Object(key).get()["Body"].read()
        return pickle.loads(serialized_value)


def unset(
    key: str,
    *,
    user: Optional[str] = None,
):
    if user is None:
        user = config.ldap
    key = f"{user}/{key}"
    with _handle_missing_key_errors(key):
        _s3_bucket().delete_objects(Delete={"Objects": [{"Key": key}]})


def pop(key: str, *, user: Optional[str] = None) -> Any:
    value = get(key, user=user)
    unset(key, user=user)
    return value


def _s3_bucket():
    s3 = boto3.resource(
        service_name="s3",
        aws_access_key_id=config.store_access_key,
        aws_secret_access_key=config.store_secret_key,
        endpoint_url=config.store_endpoint,
    )
    assert config.store_bucket is not None
    return s3.Bucket(config.store_bucket)


@contextlib.contextmanager
def _handle_missing_key_errors(key: str):
    try:
        yield
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":  # type: ignore
            raise RuntimeError(f"Key {key} not found.")
        else:
            raise
