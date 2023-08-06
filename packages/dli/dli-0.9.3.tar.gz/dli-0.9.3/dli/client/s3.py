import s3fs
import os
import logging
import six

from dli.client.exceptions import DownloadDestinationNotValid, S3FileDoesNotExist
from dli.client import utils


logger = logging.getLogger(__name__)


class Client:
    """
    A wrapper client providing util methods for s3fs
    """
    def __init__(self, key, secret, token):
        self.s3fs = build_s3fs(key, secret, token)

    def download_file(self, file, destination):
        """
        Helper function to download a file as a stream from S3
        """

        # create parent directories for destination.
        if not os.path.exists(destination):
            utils.makedirs(destination, exist_ok=True)

        # We expect destination to be a directory, so check that it is one.
        if not os.path.isdir(destination):
            raise DownloadDestinationNotValid(
                "Expected destination=`%s` to be a directory" % destination
            )

        # does the file exist in s3?
        if not self.s3fs.exists(file):
            logger.warning("Attempted to download `%s` from S3 but the file does not exist", file)
            raise S3FileDoesNotExist("File at path `%s` does not exist." % file)

        # get the bucket and path to the file
        path = file.replace("s3://", "")

        # there are two possibilities
        # 1. Path is a file in s3:
        #    In this case we just download the file directy
        # 2. Path is a key/folder in s3:
        #    In this case we walk all the files and download them individually to the target folder
        # Sadly, s3fs does not expose an `isdir` function but we can determine
        # if the path is a directory or a file by using `exists()` and `walk()` in conjkunction
        children = self.s3fs.walk(path)
        # are we downloading an specific file?
        if not children:
            self.s3fs.get(file, os.path.join(destination, os.path.basename(path)))
            return

        # otherwise we are downloading a directory
        for file in children:
            # get the relative path on where to download the file
            name = os.path.relpath(file, path)
            dest = os.path.join(destination, name)
            # create parent directories for destination.
            utils.makedirs(os.path.dirname(dest), exist_ok=True)
            # download the file
            self.s3fs.get(file, dest)

    def upload_files_to_s3(self, files, s3_location, token_refresher=None, num_retries=3):
        """
        Upload multiple files to a specified s3 location. The basename of the
        `files` will be preserved.

        :param files: An list of filepaths
        :type files: list
        :param s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :param token_refresher: Optional Function to refresh S3 token
        :param num_retries: Optional Number of retries in case of upload failure.
        :return: List of path to the files in S3
        """
        def upload(file, s3_location):
            logger.info("Uploading %s to %s", file, s3_location)
            file_name = os.path.basename(file)
            target = "{}{}".format(s3_location, file_name)

            # upload the file
            self.s3fs.put(file, target)
            logger.info("%s uploaded successfully.", file)

            # return the file with attributes
            return {
                "path": "s3://%s" % target,
                "size": os.path.getsize(file)
            }

        def upload_or_retry(file, s3_location, on_error, retries):
            try:
                return upload(file, s3_location)
            except Exception as e:
                logger.exception("Failed to upload file to S3: %s", e)

                if retries > 0:
                    on_error()
                    return upload_or_retry(file, s3_location, on_error, retries - 1)
                else:
                    raise e

        def on_error():
            if token_refresher:
                s3_access_keys = token_refresher()
                self.s3fs = build_s3fs(
                    key=s3_access_keys['accessKeyId'],
                    secret=s3_access_keys['secretAccessKey'],
                    token=s3_access_keys['sessionToken']
                )

        files_to_upload = self._files_to_upload_flattened(files)
        result = []
        for file in files_to_upload:
            uploaded = upload_or_retry(
                file,
                s3_location,
                on_error,
                num_retries
            )

            result.append(uploaded)

        return result

    def _files_to_upload_flattened(self, files):
        files_to_upload = []

        for file in files:
            if not os.path.exists(file):
                raise Exception('File / directory specified (%s) for upload does not exist.' % file)

            if os.path.isfile(file):
                logger.info("detected file: %s", file)
                files_to_upload.append(file)
            elif os.path.isdir(file):
                logger.info("detected directory: %s", file)
                files_to_upload.extend([
                    "{}/{}".format(file, f) for f in os.listdir(file) if os.path.isfile('{}/{}'.format(file, f))
                ])

        return files_to_upload


def build_s3fs(key, secret, token):
    """
    Factory function to create an s3fs client.
    Extracted as a function so that it can
    be easily mocked / patched.
    """
    return s3fs.S3FileSystem(key=key, secret=secret, token=token)


class S3DatasetWrapper:
    def __init__(self, dataset, s3fs):
        # we want to override the files property
        # it isn't really needed for py3 but it is in py2
        self.__dict__ = {
            k: v for k,v in six.iteritems(dataset) if k != "files"
        }
        self._dataset = dataset
        self._s3 = s3fs


    def __getitem__(self, path):
        """
        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance
        """
        return self.open_file(path)

    def open_file(self, path):
        """
        Helper method to load an specific file inside a dataset
        without having to download all of it.

        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance that can be used as a normal python file
        """
        if not self._s3.exists(path):
            raise S3FileDoesNotExist(path)

        return self._s3.open(path, mode='rb')

    def __repr__(self):
        return str(dict(self._dataset))

    @property
    def files(self):
        """
        Lists all S3 files in this dataset, recursing on folders (if any)
        """
        result = []
        files = [file["path"] for file in self._dataset["files"]]

        for file in files:
            children = self._s3.walk(file)

            # are we downloading an specific file?
            if not children:
                result.append(file.replace("s3://", ""))
                continue

            result.extend(children)

        return result
