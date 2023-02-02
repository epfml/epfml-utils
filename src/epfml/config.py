import os

store_access_key = os.getenv("EPFML_STORE_S3_ACCESS_KEY", None)
store_secret_key = os.getenv("EPFML_STORE_S3_SECRET_KEY", None)
store_endpoint = os.getenv("EPFML_STORE_S3_ENDPOINT", None)
store_bucket = os.getenv("EPFML_STORE_S3_BUCKET", None)
ldap = os.getenv("EPFML_LDAP", os.getenv("USER", None))
