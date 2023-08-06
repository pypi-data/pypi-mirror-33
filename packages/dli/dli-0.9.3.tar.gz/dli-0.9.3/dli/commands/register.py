from .base import Base
import os
import yaml
from datetime import datetime
import dli.datalake_api as api
import s3fs
import sys
from dli.client import session


class Register(Base):
    __s3 = s3fs.S3FileSystem()
    """Register a package."""

    def __init__(self, *args):
        super().__init__(*args)

    def run(self):
        raise Exception("cli functionality is not yet implemented. Use dli.client in a python programme instead.")

    def register_package(self, conf):
        raise Exception("cli functionality is not yet implemented. Use dli.client in a python programme instead.")

    def register_dataset(self, conf):
        raise Exception("cli functionality is not yet implemented. Use dli.client in a python programme instead.")
