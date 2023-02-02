import os

keyval_access_key = os.getenv("MLO_KEYVAL_S3_ACCESS_KEY", None)
keyval_secret_key = os.getenv("MLO_KEYVAL_S3_SECRET_KEY", None)
keyval_endpoint = os.getenv("MLO_KEYVAL_S3_ENDPOINT", None)
keyval_bucket = os.getenv("MLO_KEYVAL_S3_BUCKET", None)
default_user = os.getenv("MLO_LDAP", os.getenv("USER", None))
