import os

store_access_key = os.getenv("EPFML_STORE_S3_ACCESS_KEY", None)
store_secret_key = os.getenv("EPFML_STORE_S3_SECRET_KEY", None)
store_endpoint = os.getenv("EPFML_STORE_S3_ENDPOINT", None)
store_bucket = os.getenv("EPFML_STORE_S3_BUCKET", None)
ldap = os.getenv("EPFML_LDAP", os.getenv("USER", None))


def assert_store_is_configured():
    if (
        store_access_key is None
        or store_secret_key is None
        or store_endpoint is None
        or store_bucket is None
        or ldap is None
    ):
        raise RuntimeError(
            "Missing environment variables. "
            "Please set EPFML_STORE_S3_ACCESS_KEY, EPFML_STORE_S3_SECRET_KEY, EPFML_STORE_S3_ENDPOINT, EPFML_STORE_S3_BUCKET and EPFML_LDAP. "
            "You can get the values from a team mate."
        )
